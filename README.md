# Nonogram Game
## General Information
If you want to know more about nonograms, you can find more information on Wikipedia.   
An information about the number of possibilities $P$ to distribute k blocks with the respective length $n_i$ on N fields is given by:

$$P=\frac{(k+q-1)!}{k!(q-1)!}$$
where $q$ is given by: $$q=N-(k-2)-\sum_{i=1}^{k}n_i$$

## Quick Start
This small Python script, based on Pygame, can be used to solve nonograms by hand or automatically.

When starting the script you get a small GUI with two enabled open buttons, to open a new, empty nonogram or to open an already (partly) solved one. A right-click opens a pull-down menu that shows the most recently opened files

![](\Docs\OpenGUI.png "Open GUI")

The file format of a new nonogram is a text file with one line for each row and one line for each column of the nonogram. Row lines start with 'Z' (upper or lower case), column lines with 'S' (upper or lower case) followed by the block lengths. For example, if the first row of the nonogram has two blocks with lengths 3 and 8, the file entry for this row would be is Z 3 8.   
The file extension of new nonograms is *.nob*, partly solved have *.nos*

Some nonograms are given in the '*Nono_Examples*' folder. 

After selecting a valid file the nonogram will be displayed on the GUI.

A left mouse click sets a field to black. With a right mouse click a cross will be set and the middle mousebutton  clears the field. You can enter a trial (lower left button) mode to test some moves. In this mode the blocks and crosses will be drawn in red. If you think the red block are correct you can turn all red blocks to black (second lower button). The third lower button deletes all red trial blocks and crosses.

When clicking left on a block length value (left / above the nonogram board) it will be marked with a cross to set this  block as completed. With a right click the cross can be removed.

Following key shortcuts are available:

Key | Function
---|---
T| Change to trial mode
N | Change to normal mode
Ctrl + W | Clear all red blocks/crosses
Ctrl + B | Set all red blocks/crosses to black
Ctrl + Z | Undo
Ctrl + Y | Redo
Ctrl + A | Fill all overlapping blocks
Ctrl + R | Check if blocks/crosses can be set in partially filled rows
Ctrl + C | Check if blocks/crosses can be set in partially filled columns
Ctrl + S | Solve the nonogram


>Remark: By pressing [Ctrl + A] and alternately [Ctrl + R] and [Ctrl + C], the nonogram will successively be solved

## Configuration Data
Some user input data (recently opened file, starting directory, ...) will be saved within the environment folder using `os.environ['APPDATA']` extendet with  *"/username/nonogramm"*. For Windows this will be the directory:

   "*c:\Users\username\AppData\Roaming\username\Nonogramm*".

I do not know what happens on a Linux or Mac OS. If saving files at that location is not desired, the name can be changed in the module "*ConfigProperties.py*" 


