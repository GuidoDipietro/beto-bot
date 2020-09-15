# Beto

<hr>

Private Discord bot that remembers definitions and exam dates, thought to help myself and colleagues when using Discord as a main chatting channel for study purposes (and maybe some memeing too).

# Commands and usage
Using _relaxed_ RegExps. (That is, not formal RegExps, just some "pseudo" ones that convey the meaning of the command more directly). 

<hr>

## Help

#### ``` beto help command? ```  
If there is no ```command``` given, Beto will tell you all the commands he can handle.  
Otherwise, he will spit the usage of the command you'd like help for.  

## Private commands
Each user has their own allocated storage for these two commands and can only use their own.  

#### ``` beto acordate "<thing>" "<definition>" ```  
Meaning ```beto remember "<thing>" "<definition>"```.  
Beto will remember whatever you name as "thing", with the definition you provide.  
The parameters ```thing``` and ```definition``` should include the double quotes, unless they are single-word tokens (then it's optional).  

#### ``` beto contame (todo|"<thing>") ```  
Meaning ```beto tell me everything|"<thing>"```.  
If the message is exactly ```"beto contame todo"```, Beto will spit the names of the facts that you have told him using the ```acordate``` command.  
Otherwise, replace ```"thing"``` with the name of one of those facts and Beto will tell you the definition provided by you before.  

Again, double quotes are mandatory only if ```thing``` is not a single-word token.  

## Public commands
These two commands modify information that is common for everyone.

<hr>

#### ``` beto setfecha recu? (1|2) <materia> dd/mm ```  
```Recu``` is short for ```recuperatorio``` which means "make-up exam". Hopefully we won't use that keyword too often.  
```Materia``` means ```subject```.  
Beto will set a date for the exam if you tell him:  
- Is it a make-up?
- Is it the 1st or 2nd instance?
  - Supported values for 1: ```primero, primer, 1ero, 1er, 1```
  - Supported values for 2: ```segundo, 2do, 2```
- Subject name
- Date in dd/mm format (RegExp if you're curious: ```[0-9]{1,2}/[0-9]{1,2}```)

#### ``` beto getfecha recu? (1|2) <materia> ```  
Same as ```setfecha``` but without the date as a parameter.  
Given all those parameters, Beto will tell you what date you saved using ```setfecha``` (if any).  
