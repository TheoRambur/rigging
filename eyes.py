import maya.cmds as cmds


def snapObj(obj1, obj2, stay=1, jnt=0):
    prt = cmds.listRelatives(obj1, parent=1)
    cmds.parent(obj1, obj2)
    cmds.setAttr(obj1+".translate", 0,0,0, type="float3")
    cmds.setAttr(obj1+".rotate", 0,0,0, type="float3")
    if jnt:
        cmds.setAttr(obj1+".jointOrient", 0,0,0, type="float3")
        
    if not stay:
        if prt:
            cmds.parent(obj1, prt)
        else:
            cmds.parent(obj1, world=1)
            
            
def createLids(side):
    ref = "eye_jnt"+side
    
    upper = "upperLid_crv"+side
    lower = "lowerLid_crv"+side
    prt = "eyelid_gp"+side
    up = cmds.createNode("transform", name="lidUp_null"+side)
    snapObj(up, "eyeUp_null"+side, stay=0)
    cmds.parent(up, prt)
    
    for lid in ["upper", "lower"]:
        for i in range(0,13):
            poc = cmds.createNode("pointOnCurveInfo", name=lid+"Lid"+str(i)+"_poc"+side)
            null = cmds.createNode("transform", name=lid+"Lid"+str(i)+"_null"+side)
            cmds.parent(null, prt)
            cmds.connectAttr(lid+"Lid_crv"+side+"Shape.local", poc+".inputCurve")
            cmds.connectAttr(poc+".position", null+".translate")
            cmds.setAttr(poc+".parameter", i)
            
            cmds.select(clear=1)
            jnt = cmds.createNode("joint", name=lid+"Lid"+str(i)+"_jnt"+side)
            cmds.setAttr(jnt+".radius", .5)
            snapObj(jnt, ref, stay=0, jnt=1)
            cmds.select(clear=1)
            eff = cmds.createNode("joint", name=lid+"LidEnd"+str(i)+"_jnt"+side)
            cmds.setAttr(eff+".radius", .5)
            snapObj(eff, jnt, jnt=1)
            cmds.setAttr(eff+".translateX", 4)
            cmds.parent(jnt, prt)
            cmds.aimConstraint(null, jnt, wut="object", wuo=up, aim=(1,0,0), u=(0,1,0))
            
def createObjOffset(i, nOff = "Offset"):
    iParent = cmds.listRelatives(parent=1)
    namePart = i.split("_")
    if len(namePart) == 2:
        offName = i+nOff
    else:
        offName = namePart[0]+"_"+namePart[1]+nOff+"_"+namePart[2]
    off = cmds.createNode("transform", name=offName)
    
    cmds.parent(off, i)
    cmds.setAttr(off+".rotate", 0,0,0,type="float3")
    cmds.setAttr(off+".translate", 0,0,0,type="float3")
    if not iParent:
        cmds.parent(off, w=1)
    else:
        cmds.parent(off, iParent)
    cmds.parent(i, off)
            
def createCurveSys(side):
    gp = "eyelid_gp"+side
    clsGp = "lidCls_gp"+side
    midUp = "upperLidMid_ctr"+side
    midLow = "lowerLidMid_ctr"+side
    eyeOrient = "eyeOrient_ctr"+side

    upper = "upperLid_crv"+side
    lower = "lowerLid_crv"+side
    closedUp = "upperLidClosed_crv"+side
    closedLow = cmds.duplicate(closedUp, name="lowerLidClosed_crv"+side)[0]
    upDriver = cmds.duplicate(upper, name="upperLidDriver_crv"+side)[0]
    lowDriver = cmds.duplicate(lower, name="lowerLidDriver_crv"+side)[0]
    
    eyeRef = "eyeRef_null"+side
    eyePos = cmds.createNode("transform", n="eyePosition_null"+side)
    snapObj(eyePos, eyeRef)
    cmds.parent(eyePos, clsGp)    
    
    
    upCtr = cmds.rebuildCurve(upper, ch=0, rpo=0, rt=0, end=1, kr=0, kcp=0, kep=1, kt=1, s=3, d=2, tol=0.01, name="upperLidCtr_crv"+side)
    lowCtr = cmds.rebuildCurve(lower, ch=0, rpo=0, rt=0, end=1, kr=0, kcp=0, kep=1, kt=1, s=3, d=2, tol=0.01, name="lowerLidCtr_crv"+side)
    closedUpCtr = cmds.rebuildCurve(closedUp, ch=0, rpo=0, rt=0, end=1, kr=0, kcp=0, kep=1, kt=1, s=3, d=2, tol=0.01, name="upperLidClosedCtr_crv"+side)
    closedLowCtr = cmds.duplicate(closedUpCtr, name="lowerLidClosedCtr_crv"+side)
    
    cmds.parent(upCtr, gp)
    cmds.parent(lowCtr, gp)
    cmds.parent(closedUpCtr, gp)
    cmds.parent(closedLowCtr, gp)
    
    cmds.blendShape(upDriver, closedUp, upper, name="upperLid_bds"+side)
    cmds.blendShape(lowDriver, closedLow, lower, name="lowerLid_bds"+side)
    
    cmds.wire(upDriver, gw=False, en=1.000000, ce=0.000000, li=0.000000, w=upCtr)
    cmds.wire(lowDriver, gw=False, en=1.000000, ce=0.000000, li=0.000000, w=lowCtr)
    cmds.wire(closedUp, gw=False, en=1.000000, ce=0.000000, li=0.000000, w=closedUpCtr)
    cmds.wire(closedLow, gw=False, en=1.000000, ce=0.000000, li=0.000000, w=closedLowCtr)
    
    for crv in ["upper", "lower"]:
        val = -3
        if crv == "lower":
            val = -1
        rng = cmds.createNode("setRange", name=crv+"Lid_rng"+side)
        cmds.connectAttr(crv+"LidMid_ctr"+side+".translateY", rng+".valueX")
        cmds.setAttr(rng+".minX", 1)
        cmds.setAttr(rng+".maxX", 0)
        cmds.setAttr(rng+".oldMinX", val)
        cmds.setAttr(rng+".oldMaxX", 0)
        cmds.connectAttr(rng+".outValueX", crv+"Lid_bds"+side+"."+crv+"LidClosed_crv"+side)
        rev = cmds.createNode("reverse", name=crv+"Lid_rev"+side)
        cmds.connectAttr(rng+".outValueX", rev+".inputX")
        cmds.connectAttr(rev+".outputX", crv+"Lid_bds"+side+"."+crv+"LidDriver_crv"+side)
    
    for crv in ["upperLidCtr", "lowerLidCtr", "upperLidClosedCtr", "lowerLidClosedCtr"]:
        for i in range(0,5):
            cmds.cluster(crv+"_crv"+ side + ".cv[" + str(i) + "]", n=crv+str(i)+"_cls"+side)
            cmds.parent(crv+str(i)+"_cls"+side+"Handle", clsGp)
            createObjOffset(crv+str(i)+"_cls"+side+"Handle")
            
    
    for lid in ["upper", "lower"]:
        cmds.connectAttr(lid+"LidMid_ctr"+side+".translateX", lid+"LidCtr2_cls"+side+"Handle.translateX")
        cmds.connectAttr(lid+"LidMid_ctr"+side+".translateX", lid+"LidClosedCtr2_cls"+side+"Handle.translateX")
        
        clsRef = cmds.createNode("transform", n=lid+"LidCtr2Driven_null"+side)
        snapObj(clsRef, eyePos)
        cmds.parent(lid+"LidCtr2_clsOffset"+side+"Handle", clsRef)
        cmds.parent(lid+"LidClosedCtr2_clsOffset"+side+"Handle", clsRef)
        pbLid = cmds.createNode("pairBlend", n=lid+"LidCtr2_pbd"+side)
        cmds.connectAttr(eyeRef+".rotate", pbLid+".inRotate2")
        cmds.connectAttr(pbLid+".outRotate", clsRef+".rotate")
        cmds.connectAttr("eyeOrient_ctr"+side+"."+lid+"Follow", pbLid+".weight")
        fMult = cmds.createNode("multiplyDivide", n=lid+"SideFollow_mlt"+side)
        cmds.connectAttr("eyeOrient_ctr"+side+"."+lid+"Follow", fMult+".input1X")
        cmds.setAttr(fMult+".input2X", .5)
        
        for i in ["1","3"]:
            wCt = "In"
            if i == "3":
                wCt = "Out"
            
            mlt = cmds.createNode("multiplyDivide", name=lid+"Lid"+i+"_mlt"+side)
            cmds.connectAttr(lid+"LidMid_ctr"+side+".translateX", mlt+".input1X")
            cmds.setAttr(mlt+".input2X", 0.5)
            
            for o in ["", "Closed"]:
                
                pma = cmds.createNode("plusMinusAverage", name=lid+"Lid"+o+wCt+"_pma"+side)
                cmds.connectAttr(lid+"Lid"+wCt+"_ctr"+side+".translate", pma +".input3D[0]")
                
                if lid == "lower":
                    yRev = cmds.createNode("multiplyDivide", n=lid+"Lid"+wCt+o+"Ctr"+i+"Y_mlt"+side)
                    cmds.connectAttr(lid+"Lid"+wCt+"_ctr"+side+".translateY", yRev+".input1X")
                    cmds.setAttr(yRev+".input2X", -1)
                    cmds.connectAttr(yRev+".outputX", pma +".input3D[0].input3Dy")
                
                cmds.connectAttr(mlt+".outputX", pma +".input3D[1].input3Dx")
                
                cmds.connectAttr(pma+".output3D", lid+"Lid"+o+"Ctr"+i+"_cls"+side+"Handle.translate")
                if o == "Closed":
                    tRev = cmds.createNode("reverse", n=lid+"Lid"+o+"Ctr"+i+"_rev"+side)
                    cmds.connectAttr(lid+"LidMid_ctr"+side+".tight", tRev+".inputX")
                    cmds.connectAttr(tRev+".outputX", lid+"Lid"+o+"Ctr"+i+"_cls"+side+".envelope")
                    
            clsRef = cmds.createNode("transform", n=lid+"Lid"+"Ctr"+i+"Driven_null"+side)
            snapObj(clsRef, eyePos)
            cmds.parent(lid+"LidCtr"+i+"_clsOffset"+side+"Handle", clsRef)
            cmds.parent(lid+"Lid"+o+"Ctr"+i+"_clsOffset"+side+"Handle", clsRef)
            pbLid = cmds.createNode("pairBlend", n=lid+"LidCtr"+i+"_pbd"+side)
            cmds.connectAttr(eyeRef+".rotate", pbLid+".inRotate2")
            cmds.connectAttr(pbLid+".outRotate", clsRef+".rotate")
            cmds.connectAttr(fMult+".outputX", pbLid+".weight")
        
                
   
    for s in ["In", "Out"]:
        n = "0"
        if s == "Out":
            n = "4"
        for lid in ["upper","lower"]:
            for o in ["", "Closed"]:
                cmds.connectAttr("lidCorner"+s+"_ctr"+side+".translate", lid+"Lid"+o+"Ctr"+n+"_cls"+side+"Handle.translate")
                
    #attach controlers
                
    for lid in ["upper","lower"]:
        crv = lid+"Lid_crv"+side
        pocMid = cmds.createNode("pointOnCurveInfo", name=lid+"LidForCtr_poc"+side)
        cmds.connectAttr(crv+".local", pocMid+".inputCurve")
        cmds.setAttr(pocMid+".parameter", 6)
        cmds.connectAttr(pocMid+".position", lid+"LidMid_ctrDriven"+side+".translate")
        
        for s in ["In","Out"]:
            par1 = 3
            if s == "Out":
                par1 = 9
            poc = cmds.createNode("pointOnCurveInfo", name=lid+"LidForCtr"+s+"_poc"+side)
            cmds.connectAttr(crv+".local", poc+".inputCurve")
            cmds.setAttr(poc+".parameter", par1)
            cmds.connectAttr(poc+".position", lid+"Lid"+s+"_ctrDriven"+side+".translate")
            
    for s in ["In", "Out"]:
        par2 = 0
        if s == "Out":
            par2 = 12
            
        poc = cmds.createNode("pointOnCurveInfo", name="lidCornerForCtr"+s+"_poc"+side)
        cmds.connectAttr(crv+".local", poc+".inputCurve")
        cmds.setAttr(poc+".parameter", par2)
        cmds.connectAttr(poc+".position", "lidCorner"+s+"_ctrDriven"+side+".translate")
        
        
    #lids follow
    
    
        
     
    

createCurveSys("_L")




def reverseCtrl():
    sel = cmds.ls(sl=1)
    
    for obj in sel:
        nComp = obj.split("_")
        cmds.select(obj)
        createOffset(nOff="Reversed")
        mlt = cmds.createNode("multiplyDivide", name=nComp[0]+"Ctr_mlt_"+nComp[-1])
        cmds.connectAttr(obj+".translate", mlt+".input1")
        cmds.setAttr(mlt+".input2", -1,-1,-1,type="float3")
        cmds.connectAttr(mlt+".output", nComp[0]+"_"+nComp[1]+"Reversed_"+nComp[3]+".translate")
        
        
        
def attachCtrl(side):

    for lid in ["upper","lower"]:
        crv = lid+"Lid_crv"+side
        pocMid = cmds.createNode("pointOnCurveInfo", name=lid+"LidForCtr_poc"+side)
        cmds.connectAttr(crv+".local", pocMid+".inputCurve")
        cmds.setAttr(pocMid+".parameter", 6)
        cmds.connectAttr(pocMid+".position", lid+"LidMid_ctrDriven"+side+".translate")
        
        for s in ["In","Out"]:
            par1 = 3
            if s == "Out":
                par1 = 9
            poc = cmds.createNode("pointOnCurveInfo", name=lid+"LidForCtr"+s+"_poc"+side)
            cmds.connectAttr(crv+".local", poc+".inputCurve")
            cmds.setAttr(poc+".parameter", par1)
            cmds.connectAttr(poc+".position", lid+"Lid"+s+"_ctrDriven"+side+".translate")
            
    for s in ["In", "Out"]:
        par2 = 0
        if s == "Out":
            par2 = 12
            
        poc = cmds.createNode("pointOnCurveInfo", name="lidCornerForCtr"+s+"_poc"+side)
        cmds.connectAttr(crv+".local", poc+".inputCurve")
        cmds.setAttr(poc+".parameter", par2)
        cmds.connectAttr(poc+".position", "lidCorner"+s+"_ctrDriven"+side+".translate")
            
            
            
attachCtrl("_L")
            
        

def createLidSec(side):
    gp = cmds.createNode("transform", n="notchJnt_gp"+side)
    gpNull = cmds.createNode("transform", n="notchNull_gp"+side)
    cmds.parent(gpNull, "eyelid_gp"+side)
    cmds.parent(gp, "eyelid_gp"+side)
    crv = cmds.duplicate("upperLid_crv"+side, n="notch_crv"+side)[0]
    crvDvn = cmds.duplicate("upperLidCtr_crv"+side, n="notchDriven_crv"+side)[0]
    crvDvr= cmds.duplicate("upperLidCtr_crv"+side, n="notchDriver_crv"+side)[0]
    
    cmds.wire(crvDvr, gw=False, en=1.000000, ce=0.000000, li=0.000000, w="upperLid_crv"+side, dds=0)
    cmds.wire(crv, gw=False, en=1.000000, ce=0.000000, li=0.000000, w=crvDvn)
    
    for i in range(0, 13):
        cmds.select(clear=1)
        jnt = cmds.createNode("joint", n="notch"+str(i)+"_jnt"+side)
        jnt2 = cmds.createNode("joint", n="notchEnd"+str(i)+"_jnt"+side)
        cmds.parent(jnt2, jnt)
        snapObj(jnt, "upperLid"+str(i)+"_jnt"+side, jnt=1, stay=0)
        cmds.setAttr(jnt2+".translateX", cmds.getAttr("upperLidEnd"+str(i)+"_jnt"+side+".translateX"))
        cmds.parent(jnt, gp)
        null = cmds.createNode("transform", n="notch"+str(i)+"_null"+side)
        cmds.parent(null, gpNull)
        poc = cmds.createNode("pointOnCurveInfo", n="notch"+str(i)+"_poc"+side)
        cmds.connectAttr(crv+".local", poc+".inputCurve")
        cmds.setAttr(poc+".parameter", i)
        cmds.connectAttr(poc+".position", null+".translate")
        
        cmds.aimConstraint(null, jnt, wut="object", wuo="lidUp_null"+side, aim=(1,0,0), u=(0,1,0))
        
    mltGb = cmds.createNode("multiplyDivide", n="notchPushed_mlt"+side)
    for ax in ["X","Y","Z"]:
        cmds.connectAttr("eyebrow_ctr"+side+".pushesLid", mltGb+".input1"+ax)
        
    rev = cmds.createNode("reverse", n="notch_rev"+side)
    cmds.connectAttr(mltGb+".output", rev+".input")

    
    crvInfo = cmds.createNode("curveInfo", n="notch_cif"+side)
    cmds.connectAttr(crvDvr+".local", crvInfo+".inputCurve")
    crvInfoUp = cmds.createNode("curveInfo", n="upperLid_cif"+side)
    cmds.connectAttr("upperLidCtr_crv"+side+".local", crvInfoUp+".inputCurve")
    
    for i in range(0,5):
        cmds.cluster(crvDvn+".cv[" + str(i) + "]", n="notch"+str(i)+"_cls"+side)
        createObjOffset("notch"+str(i)+"_cls"+side+"Handle", nOff = "Offset")
        clsDrv = cmds.createNode("transform", n="notch"+str(i)+"ClsDriver_null"+side)
        for axe in ["X", "Y", "Z"]:
            cmds.setAttr(clsDrv+".translate"+axe, cmds.getAttr("notch"+str(i)+"_cls"+side+"Handle.rotatePivot"+axe))
        cmds.parent("notch"+str(i)+"_clsOffset"+side+"Handle", clsDrv)
        cmds.parent(clsDrv, "lidCls_gp"+side)
        s = "X"
        if side == "_R":
            s = "Y"
            
        ax = ""
        if i == 0 or i == 1:
            ax = "X"
        elif i == 2:
            ax ="Y"
        elif i == 3 or i == 4:
            ax = "Z"
        
        if ax == "X":
            cmds.connectAttr("eyebrowsDown_rng.outValue"+s, mltGb+".input2"+ax, f=1)
        elif ax == "Y":
            cmds.connectAttr("eyebrowsMidDown_rng"+side+".outValueX", mltGb+".input2"+ax, f=1)
        elif ax == "Z":
            cmds.connectAttr("eyebrowsOutDown_rng"+side+".outValueX", mltGb+".input2"+ax, f=1)
            
            
        pma = cmds.createNode("plusMinusAverage", n="notch"+str(i)+"_pma"+side)
        mltUp = cmds.createNode("multiplyDivide", n="notchUp"+str(i)+"_mlt"+side)
        mltDown = cmds.createNode("multiplyDivide", n="notchDown"+str(i)+"_mlt"+side)
        
        cmds.connectAttr(crvInfo+".controlPoints["+str(i)+"]", mltDown+".input1")
        cmds.connectAttr(crvInfoUp+".controlPoints["+str(i)+"]", mltUp+".input1")
        cmds.connectAttr(mltUp+".output", pma+".input3D[0]")
        cmds.connectAttr(mltDown+".output", pma+".input3D[1]")
        
        for axe in ["X","Y","Z"]:
            cmds.connectAttr(mltGb+".output"+ax, mltDown+".input2"+axe)
            cmds.connectAttr(rev+".output"+ax, mltUp+".input2"+axe)
            
        cmds.connectAttr(pma+".output3D", clsDrv+".translate")
            

        
createLidSec("_L")
createLidSec("_R")



def updateLidSec(side):
    for i in range(0,13):
        mlt = cmds.createNode("multiplyDivide", n="notch"+str(i)+"_mlt"+side)
        cmds.connectAttr("upperLid"+str(i)+"_jnt"+side+".rotate", mlt+".input1")
        cmds.connectAttr(mlt+".output", "notch"+str(i)+"_jnt"+side+".rotate")
        pma = cmds.createNode("plusMinusAverage", n="notch"+str(i)+"_pma"+side)
        for ax in ["X","Y","Z"]:
            cmds.connectAttr(pma+".output1D", mlt+".input2"+ax)
        
        mltAvg = cmds.createNode("multiplyDivide", n="notch"+str(i)+"Avg_mlt"+side)
        mltGb = cmds.createNode("multiplyDivide", n="notchGb"+str(i)+"_mlt"+side)
        s = "X"
        if side == "_R":
            s = "Y"
            
        cmds.connectAttr("lidPush_rng.outValue"+s, mltGb+".input1X")
        cmds.connectAttr("lidPush_rng.outValue"+s, mltGb+".input1Y")
        
        if i <= 6:
            s = "X"
            if side == "_R":
                s = "Y"
            cmds.connectAttr("eyebrowsDown_rng.outValue"+s, mltAvg+".input1X")
            cmds.connectAttr("eyebrowsMidDown_rng"+side+".outValueX", mltAvg+".input1Y")
            cmds.setAttr(mltAvg+".input2X", 1.-((1./6.)*float(i)))
            cmds.setAttr(mltAvg+".input2Y", (1./6.)*float(i))
            
        else:
            cmds.connectAttr("eyebrowsMidDown_rng"+side+".outValueX", mltAvg+".input1X")
            cmds.connectAttr("eyebrowsOutDown_rng"+side+".outValueX", mltAvg+".input1Y")
            cmds.setAttr(mltAvg+".input2X", 1.-((1./6.)*float(i-6)))
            cmds.setAttr(mltAvg+".input2Y", (1./6.)*float(i-6))
            
        cmds.connectAttr(mltAvg+".outputX", mltGb+".input2X")
        cmds.connectAttr(mltAvg+".outputY", mltGb+".input2Y")
        
        cmds.connectAttr(mltGb+".outputX", pma+".input1D[0]")
        cmds.connectAttr(mltGb+".outputY", pma+".input1D[1]")
        
        
            
updateLidSec("_L")
updateLidSec("_R")






















