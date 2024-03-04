import maya.cmds as cmds

def createObjOffset(obj, nOff = "Offset"):
    iParent = cmds.listRelatives(obj, parent=1)
    namePart = obj.split("_")
    if len(namePart) == 2:
        offName = obj+nOff
    else:
        offName = namePart[0]+"_"+namePart[1]+nOff+"_"+namePart[2]
    off = cmds.createNode("transform", name=offName)
    
    cmds.parent(off, obj)
    cmds.setAttr(off+".rotate", 0,0,0,type="float3")
    cmds.setAttr(off+".translate", 0,0,0,type="float3")
    cmds.setAttr(off+".scale", 1,1,1,type="float3")
    if not iParent:
        cmds.parent(off, w=1)
    else:
        cmds.parent(off, iParent)
    cmds.parent(obj, off)

def snapObj(obj1, obj2):
    cmds.parent(obj1, obj2)
    cmds.setAttr(obj1+".rotate", 0,0,0,type="float3")
    cmds.setAttr(obj1+".translate", 0,0,0,type="float3")
    
def snapJnt(jnt1, jnt2):
    cmds.parent(jnt1, jnt2)
    cmds.setAttr(jnt1+".rotate", 0,0,0,type="float3")
    cmds.setAttr(jnt1+".translate", 0,0,0,type="float3")
    cmds.setAttr(jnt1+".jointOrient", 0,0,0,type="float3")
    
def thinJnt(name):
    jnt = cmds.createNode("joint", name=name)
    cmds.setAttr(jnt+".radius", .2)
    return jnt
    
    
def createSecBlending(obj, oAtt, driver, dAtt, pos, rot):
    drvName = driver.split("_")
    bName = drvName[0]
    side = ""
    if len(drvName) == 3:
        side = "_"+drvName[2]
        
    rng =  cmds.createNode("setRange", name=bName+"_rng"+side)
    axe = ["X","Y","Z"]
    id = 0
    for jnt in obj:
        cmds.connectAttr(driver+"."+dAtt, rng+".value"+axe[id])
        cmds.setAttr(rng+".min"+axe[id], pos[id][0])
        cmds.setAttr(rng+".max"+axe[id], pos[id][1])
        cmds.setAttr(rng+".oldMin"+axe[id], rot[id][0])
        cmds.setAttr(rng+".oldMax"+axe[id], rot[id][1])
        cmds.connectAttr(rng+".outValue"+axe[id], jnt+"."+oAtt)
        id += 1

    
def createFingerCtrl(f, w, side):
    prt = "fingersCtr_gp"+side
    fng = f+w+"_jnt"+side
        
    ctrl = cmds.duplicate("fingerCtrProxy", name=f+w+"_ctr"+side)[0]
    snapObj(ctrl, fng)
    cmds.parent(ctrl, prt)
    createObjOffset(ctrl)
    
    if w == "Meta":
        pma = cmds.createNode("plusMinusAverage", n=f+w+"_pma"+side)
        #cmds.connectAttr(ctrl+".translate", fng+".translate")
        cmds.connectAttr(ctrl+".rotate", pma+".input3D[0]")
        cmds.connectAttr(pma+".output3D", fng+".rotate")
        #cmds.parentConstraint(ctrl, fng)
        
    else:
        cmds.connectAttr(ctrl+".rotate", fng+".rotate")
    
    return f+w+"_ctrOffset"+side
    
    
    

def createFingerAvg(f, w, side):

    cmds.select(clear =1)
    fng = f+w+"_jnt"+side
    baseParent = cmds.listRelatives(fng, parent=1)
    baseJnt = thinJnt(name=f+w+"avg_jnt"+side)
    snapJnt(baseJnt, fng)
    cmds.parent(baseJnt, baseParent)
    pair = cmds.createNode("pairBlend", name=f+w+"_bld"+side)
    cmds.setAttr(pair+".weight",0.5)
    cmds.connectAttr(fng+".rotateZ", pair+".inRotateZ1")
    cmds.connectAttr(pair+".outRotateZ", baseJnt+".rotateZ")
    
    cmds.select(clear=1)
    upJnt = thinJnt(name=f+w+"up_jnt"+side)
    snapJnt(upJnt, baseJnt)
    cmds.setAttr(upJnt+".translateY", -0.5)
    
    cmds.select(clear=1)
    lowJnt = thinJnt(name=f+w+"low_jnt"+side)
    snapJnt(lowJnt, baseJnt)
    cmds.setAttr(lowJnt+".translateY", 0.5)
    
    cmds.select(clear=1)
    squJnt = thinJnt(name=f+w+"squash_jnt"+side)
    snapJnt(squJnt, baseParent)
    cmds.setAttr(squJnt+".translateX", (cmds.getAttr(fng+".translateX")/3.)*2.)
    
    createSecBlending([upJnt, lowJnt, squJnt], "translateY", baseJnt, "rotateZ", [[-.5,-1.5],[.5,1.5],[0,1]], [[0,45],[0,45],[0,45]] )
    
    '''if w != "Meta":
        if not (f == "thumb" and w == "A"):
            print f
            print w
            bs = "Meta"
            if w == "B": bs = "A"
            elif w == "C": bs = "B"
            baseSqu = f+bs+"squash_jnt"+side
            createSecBlending([baseSqu], "translateY", baseJnt, "rotateZ", [[0,-.5]], [[0,45]] )'''
    
    
def createMetaRoll(f,w,side):
    ctr = "fingersRot_ctr"+side
    createObjOffset(f+w+"_ctr"+side, nOff = "Driven")
    
    mlt = cmds.createNode("multiplyDivide", name=f+w+"Roll_mlt"+side)
    cmds.connectAttr(ctr+".rotateX", mlt+".input1X")
    cmds.connectAttr(ctr+".rotateY", mlt+".input1Y")
    cmds.connectAttr(ctr+".rotateX", mlt+".input1Z")
    coef = -1
    coef2 = 1
    if f == "index": 
        coef = -.1
        coef2 = .0
    elif f == "major": 
        coef = -.2
        coef2 = .33
    elif f == "annular": 
        coef = -.6
        coef2 = .66
    cmds.setAttr(mlt+".input2X", coef)
    cmds.setAttr(mlt+".input2Y", coef2)
    cmds.setAttr(mlt+".input2Z", coef2)
    cmds.connectAttr(mlt+".outputX", f+w+"_ctrDriven"+side+".rotateZ")
    cmds.connectAttr(mlt+".outputY", f+w+"_ctrDriven"+side+".rotateY")
    cmds.connectAttr(mlt+".outputZ", f+w+"_ctrDriven"+side+".rotateX")
    cmds.connectAttr(mlt+".outputX", f+w+"_pma"+side+".input3D[1].input3Dz")
    cmds.connectAttr(mlt+".outputY", f+w+"_pma"+side+".input3D[1].input3Dy")
    cmds.connectAttr(mlt+".outputZ", f+w+"_pma"+side+".input3D[1].input3Dx")
    
    
def createFingerRoll(f, side):
    ctr = "fingersRot_ctr"+side
    
    rng = cmds.createNode("setRange", name = f+"Roll_rng"+side)
    
    for w in [["A", "X"], ["B", "Y"], ["C", "Z"]]:
        coef = 90
        if f == "major": coef = 70
        elif f == "annular": coef = 50
        elif f == "pinky": coef = 30
        
        cmds.connectAttr(ctr+".rotateZ", rng+".value"+w[1])
        createObjOffset(f+w[0]+"_ctr"+side, nOff = "Driven")
        cmds.setAttr(rng+".min"+w[1], -90)
        cmds.setAttr(rng+".max"+w[1], 90)
        cmds.setAttr(rng+".oldMin"+w[1], -coef)
        cmds.setAttr(rng+".oldMax"+w[1], coef)
        cmds.connectAttr(rng+".outValue"+w[1], f+w[0]+"_pma"+side+".input3D[1].input3Dz")
        cmds.connectAttr(rng+".outValue"+w[1], f+w[0]+"_ctrDriven"+side+".rotateZ")
    

def createFingerRig(side):
    for f in ["thumb", "index", "major", "annular", "pinky"]:
        id = 0
        wl = ["Meta", "A", "B", "C"]
        for w in wl:
            if not (f == "thumb" and w == "Meta"):
                off = createFingerCtrl(f, w, side)
                if w != "Meta":
                    if not (f == "thumb" and w == "A"):
                        cmds.parent(off, f+wl[id-1]+"_ctr"+side)
                    
                    
                    createFingerAvg(f, w, side)
                else:
                    createMetaRoll(f,w,side)
                    
                #cmds.connectAttr(f+w+"_ctr"+side+".rotate", f+w+"_jnt"+side+".rotate")
            id += 1
            
        #if f != "thumb":
            #createFingerRoll(f, side)

                



createFingerRig("_L")
createFingerRig("_R")
















