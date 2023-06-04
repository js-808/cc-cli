# cp-cli: Competitive Programming Practice

*Note* 

This repo is still very much a work in progress. I expect to be working on it over the coming weeks and months. Here is a list of very vague goals I hope to accomplish before the code is actually able 
to be packaged, shipped, and used. But for now, the code is pretty much useless as it is.

*Indended Functionality*

The idea of this repository is to create a CLI that allows you to submit competitive programming
problems directly to the Kattis and UVa online judges, and get your results.

In addition, the CLI will allow 
you to download sample data (inputs and outputs) for a given problem to your local machine, and 
allow you to view the difference between your output and the provided, expected output. 

This will also provide a way to run a suite of user-created test cases all at once, 
and provide output for them (though it will not provide expected output to compare to).

Finally, the CLI will provide a way to create a folder/problem structure for practice
problems of specific chapters and sub-sections of Halim, Halim, and Effendy's "Competitive
Programming 4" book (Volumes 1 and 2), whose lists of problems in each chapter and 
sub-section have been made publically available [here](https://cpbook.net/methodstosolve). 

 

## TODO

1. ~~Create JSON representation of all the Kattis problems used in the book~~
2. ~~Combine the JSON from part (1) with the UVA problems we got from the UHunt API.~~
3. Write setup functions/classes that set up the file structure for a given chapter/sub-chapter. (Do we want to just do the whole book? NAH...)

   a. This should download appropriate sample
   code files from the appropriate website, and store them in their own direcotry

   b. This should also initialize empty code files of a selected language (if desired) in each directory, appropriately named.
4. Write functions/classes to test user code against sample cases (ability to run tests). This might actually need to be a makefile/batch script of some sort. We will see... But as for now, all we want is for the user to be able to run against all default test cases, and see the "diff" easily.

   a. Also integrate ability to write your own test cases and run them as well (perhaps just adding to the "test-cases" folder (or other named folder that I can't think of right now)?)
5. Write submit functionality for both UVA and Kattis (highly non-trivial). May need to consult other peoples' repositories for this.
6. Document the code nicely all along the way to make it easily modifiable, extendable, and maintainable.
7. Also make the code portable onto various operating systems if possible.
8. ~~Create test cases for the functionality of this package. Run the tests frequently during development in order to ensure that all requirements are being met.~~
9. ~~Set up GitHub with license file, how to contribute, GitHub actions for running tests automatically whenever a branch needs to be merged, a commit/push is run, etc.~~
10. Celebrate your success!
