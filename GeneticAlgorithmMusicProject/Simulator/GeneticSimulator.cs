using GeneticAlgorithmMusicProject.ViewModels;
using System;
using System.Collections.Generic;
using System.IO;
using System.Linq;
using System.Text;
using System.Threading.Tasks;

namespace GeneticAlgorithmMusicProject.Simulator
{
    public enum SimulationType { 
        OutputEveryGen, 
        CustomOutput
    }
    public class GeneticSimulator
    {
        public string FileName = "";
        public string OutputFolderPath = "";
        public char[] Goal;
        public int PopulationSize = 500;
        public int MutationFactor = 50;
        public char[] HeaderData;
        public int counter = 0;
        public Random random = new Random();
        public SimulationType SelectionType = SimulationType.OutputEveryGen;
        public MainViewModel MainVm { get; set; }
        //Added list of milstones to output to wave when reached certain points
        public List<int> Milestones = new List<int> { 2, 5, 10, 15, 25, 35, 50, 65, 75, 85, 90, 95, 97 };

        public void StartSimulation(string filePath, MainViewModel mainVm)
        {
            CreateOutputFolder(filePath);
            var returnedResult = GetWavFile(filePath);
            MainVm = mainVm;
            Goal = returnedResult.Item1;
            HeaderData = returnedResult.Item2;
            MainVm.UpdateCurrentSimulationStats("-", "-", "-");
            //set SelectionType value from UI
            if (SelectionType == SimulationType.CustomOutput) {
                //add Milestones to list from user input 
                //Milestones =
            }


            var watch = System.Diagnostics.Stopwatch.StartNew();
            var result = GenerateIntialPopulation();
            Tuple<Chromosome[], char[], double> result2 = null;
            Chromosome[] Population = result.Item1;
            char[] FittestChromosome = result.Item2;
            int GenerationNumber = 1;
            double averageChromoScore = 0;
            var genWatch = System.Diagnostics.Stopwatch.StartNew();
            List<Chromosome> MatingPool;

            while (FittestChromosome != Goal)
            {
                GenerationNumber++;
                MatingPool = GenerateMatingPool(Population);
                result2 = GeneratePopulationFromMatingPool(MatingPool);
                Population = result2.Item1;
                FittestChromosome = result2.Item2;
                averageChromoScore = result2.Item3;
                int fitnessPercentage = (int)Math.Round(averageChromoScore);
                MainVm.UpdateCurrentSimulationStats(GenerationNumber.ToString(), DateTime.Now.ToString(), averageChromoScore.ToString());

                if (SelectionType == SimulationType.OutputEveryGen)
                {
                    OuputToWav(FittestChromosome, averageChromoScore);
                }
                else {
                    if (Milestones.Contains(fitnessPercentage)) {
                        OuputToWav(FittestChromosome, averageChromoScore);
                    }
                }
                 watch.Stop();
                 var genMs = watch.ElapsedMilliseconds;
                 var genSeconds = genMs / 1000;
                 genWatch = System.Diagnostics.Stopwatch.StartNew();

            }

            watch.Stop();
            var elapsedMs = watch.ElapsedMilliseconds;
            var elapsedSeconds = elapsedMs / 1000;
            //Will only reach this point at 100% fitness
            OuputToWav(FittestChromosome, 100);
            Console.WriteLine("Computed In: " + GenerationNumber + " generations " + "\nFittest Chromosome: " + FittestChromosome + "\nTime taken: " + elapsedSeconds + " seconds");

        }


        public Tuple<char[], char[]> GetWavFile(string filePath)
        {
            byte[] bytes = System.IO.File.ReadAllBytes(filePath);
            string goal = "";
            string headerData = "";

            for (int i = 0; i < bytes.Length; ++i)
            {
                if (i >= 44)
                {
                    goal = goal + System.Text.Encoding.ASCII.GetString(new[] { bytes[i] }).ToString();
                }
                else
                {
                    headerData = headerData + System.Text.Encoding.ASCII.GetString(new[] { bytes[i] }).ToString();
                }

            }

            char[] headerArray = headerData.ToArray();
            char[] goalArray = goal.ToArray();
            var result = Tuple.Create<char[], char[]>(goalArray, headerArray);
            return result;
        }



        public List<Chromosome> GenerateMatingPool(Chromosome[] Population)
        {
            
            List<Chromosome> MatingPool = new List<Chromosome>();

            //Removed the foreach loop for improved speeds over large population
            for (int j = 0; j < Population.Length; ++j)
            {

                for (int i = 1; i <= Population[j].Fitness * 10; i++)
                {
                    
                    MatingPool.Add(Population[j]);
                }
            }

  
            return MatingPool;
        }

        public double FitnessCalculater(char[] Chromosome, char[] goal)
        {
            if (goal.Length > 0)
            {
                double CommonCounter = 0;
                for (int i = 0; i < Chromosome.Length; i++)
                {

                    if (Chromosome[i] == goal[i])
                    {
                        CommonCounter++;

                    }
                }

                double CommonPercentage = (CommonCounter / goal.Length) * 100;
                return CommonPercentage;
            }
            else
            {
                return 0;
            }

        }

        public char[] RandomChromosomeGenerator()
        {
            char[] newDNA = new char[Goal.Length];

            for (int i = 0; i < Goal.Length; i++)
            {
                char temp = Convert.ToChar(random.Next(0, 255));
                newDNA[i] = temp;
            }

            return newDNA;

        }

        public Tuple<Chromosome[], char[], int> GenerateIntialPopulation()
        {
            Chromosome[] Population = new Chromosome[PopulationSize];
            char[] fittestChromsome = new char[Goal.Length];
            int fittestChromosomeScore = 0;
            for (int i = 0; i < PopulationSize; i++)
            {
                Chromosome chromo = new Chromosome(RandomChromosomeGenerator(), Goal);
                Population[i] = chromo;

                if (Population[i].Fitness > fittestChromosomeScore)
                {
                    fittestChromsome = Population[i].DNA;
                }
            }
            return Tuple.Create<Chromosome[], char[], int>(Population, fittestChromsome, fittestChromosomeScore);

        }


        public Tuple<Chromosome[], char[], double> GeneratePopulationFromMatingPool(List<Chromosome> MatingPool)
        {
            //char[] Parent1;
            //char[] Parent2;
            char[] UnmutatedChild;
            char[] Child;
            double fittestChromosomeScore = 0;
            char[] fittestChromosome = new char[Goal.Length];



            double sumOfFitness = 0;
            Chromosome[] Population = new Chromosome[PopulationSize];
            for (int i = 0; i < PopulationSize; i++)
            {
                char[] Parent1 = MatingPool[random.Next(0, MatingPool.Count)].DNA;
                char[] Parent2 = MatingPool[random.Next(0, MatingPool.Count)].DNA;
                UnmutatedChild = GenerateChild(Parent1, Parent2);
                Child = Mutate(UnmutatedChild);
                Chromosome chromo = new Chromosome(Child, Goal);
                Population[i] = chromo;

                sumOfFitness = sumOfFitness + Population[i].Fitness;
                if (Population[i].Fitness > fittestChromosomeScore)
                {
                    fittestChromosome = Population[i].DNA;
                    fittestChromosomeScore = Population[i].Fitness;
                }
            }


            return Tuple.Create<Chromosome[], char[], double>(Population, fittestChromosome, sumOfFitness/PopulationSize);

        }

        public char[] GenerateChild(char[] Parent1, char[] Parent2)
        {
          
            for(int i = 0; i<Parent1.Length;i++)
            {
                
                if(Parent1[i]!=Goal[i])
                {
                  Parent1[i] = Parent2[i];
                }
                
            }

            return Parent1;

        }


        public char[] Mutate(char[] unmutatedChild)
        {
           
            
            for (int i = 0; i < MutationFactor; i++)
            {
                int BitFlip =  random.Next(0,unmutatedChild.Length); 
                unmutatedChild[BitFlip] = (Convert.ToChar(random.Next(0, 255)));               
            }

            return unmutatedChild;

        }

        public void CreateOutputFolder(string filePath) 
        {
            int idx = filePath.LastIndexOf('\\'); //find the index of the last backslash
            FileName = (filePath.Substring((idx + 1))); //get the name of the file from the last occurance of a backslash to the end of the .wav
            FileName = FileName.Substring(0, FileName.Length - 4); //remove .wav extension from the file name

            OutputFolderPath = System.IO.Path.Combine(Environment.GetFolderPath(Environment.SpecialFolder.Desktop),FileName); //create a new folder with the name of the file inputted


            if (!System.IO.Directory.Exists(OutputFolderPath))
            {
                try
                {
                    System.IO.Directory.CreateDirectory(OutputFolderPath);
                }
                catch (IOException ie)
                {
                    Console.WriteLine("IO Error: " + ie.Message);
                }
                catch (Exception e)
                {
                    Console.WriteLine("General Error: " + e.Message);
                }
            }
        }

        public void OuputToWav(char[] FittestChromosome, double fitness)
        {
            char[] FullBytes = new char[HeaderData.Length+Goal.Length];
            int iterator=0;
            for(int i = 0; i<FullBytes.Length;i++)
            {
                if(i<44)
                {
                    FullBytes[i] = HeaderData[i];
                }

                else
                {
                    FullBytes[i] = FittestChromosome[iterator];
                    iterator++;
                }
            } 
            byte[] bytes = Encoding.ASCII.GetBytes(FullBytes);
            double fitness2 = (int)Math.Round(fitness);
            //System.IO.File.WriteAllBytes(@"C:\Users\USER\Downloads\GenerationWavFiles\" + fitness2 + ".wav", bytes);
            System.IO.File.WriteAllBytes(OutputFolderPath + "\\GenerationFitnesss" + "_" + fitness2 + ".wav", bytes);
        }
       

    }
}
