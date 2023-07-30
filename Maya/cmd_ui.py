import maya.cmds as cmd

def gui():
    win_id = "bbb"
    win_title = "劲爆大象部落"
    
    if cmd.window(win_id, q=True, exists=True):
        cmd.deleteUI(win_id)
    
    window = cmd.window(win_id, title=win_title)
    rbox = cmd.rowColumnLayout(adj=True)

    cmd.frameLayout("Position:")

    array_tag = ["Min", "Mid", "Max"]
    x_axis = cmd.radioButtonGrp(label="X Position: ", labelArray3=array_tag, numberOfRadioButtons=3, data1=0, data2=1, data3=2)
    y_axis = cmd.radioButtonGrp(label="Y Position: ", labelArray3=array_tag, numberOfRadioButtons=3, data1=0, data2=1, data3=2)
    z_axis = cmd.radioButtonGrp(label="Z Position: ", labelArray3=array_tag, numberOfRadioButtons=3, data1=0, data2=1, data3=2)
    

    cmd.button(label="Set Pivot Postion")
    
    cmd.showWindow(window)


gui()