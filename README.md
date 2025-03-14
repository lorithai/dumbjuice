# dumbjuice
library to simplify sharing of python programs with non-technical people. 

It works by installing the used python version and libraries without the end users input. 

## instructions
in your python app folder create a dumbjuice.conf
if you are using any libraries and modules that require installing by pip, include that in a requirements.txt file as well

`
import dumbjuice as dj
dj.build("appfolder")
`

