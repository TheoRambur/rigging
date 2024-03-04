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

def createZipJnt():
    gp = "zipJnt_gp"
    
    for i in range(0,21):
        #null = cmds.createNode("transform", name="middleZip"+str(i)+"_null")
        #cmds.parent(null, gp)
        poc = cmds.createNode("pointOnCurveInfo", name="middleZip"+str(i)+"_poc")
        cmds.setAttr(poc+".parameter", i)
        cmds.connectAttr("middleLipBase_crvShape.local", poc+".inputCurve")
        #cmds.connectAttr(poc+".position", null+".translate")
        
    for w in ["upper", "lower"]:
        for i in range(0,21):
            cmds.select(clear=1)
            jnt = cmds.createNode("joint", name=w+"Zip"+str(i)+"_jnt")
            cmds.setAttr(jnt+".radius", .2)
            cmds.parent(jnt, gp)
            createObjOffset(jnt)
            poc = cmds.createNode("pointOnCurveInfo", name=w+"Zip"+str(i)+"_poc")
            cmds.setAttr(poc+".parameter", i)
            cmds.connectAttr(w+"LipBase_crvShape.local", poc+".inputCurve")
            cmds.connectAttr(poc+".position", w+"Zip"+str(i)+"_jntOffset.translate")
    
            pma = cmds.createNode("plusMinusAverage", name=w+"Zip"+str(i)+"_pma")
            cmds.setAttr(pma+".operation", 2)
            cmds.connectAttr("middleZip"+str(i)+"_poc.positionY", pma+".input1D[0]")
            cmds.connectAttr(w+"Zip"+str(i)+"_jntOffset.translateY", pma+".input1D[1]")
            mlt = cmds.createNode("multiplyDivide", name=w+"Zip"+str(i)+"_mlt")
            cmds.connectAttr(pma+".output1D", mlt+".input1X")
            cmds.connectAttr("lipCorner_ctr_L.zip", mlt+".input2X")
            cmds.connectAttr(mlt+".outputX", jnt+".translateY")
            
createZipJnt()
        
        
        
def inverseSkin():
    for w in ["upper", "lower"]:
        for i in range(0,21):
            jnt = w+"Zip"+str(i)+"_jnt"
            dst = cmds.listConnections(jnt+".worldMatrix[0]", s=0, d=1, p=1)[0]
            preMat = dst.replace("matrix", "bindPreMatrix")
            cmds.connectAttr(jnt+"Offset.inverseMatrix", preMat)
            
import maya.cmds as cmds

def createZipSystemAlone():
    gp = "zipJnt_gp"
    
    for i in range(0,21):
        #null = cmds.createNode("transform", name="middleZip"+str(i)+"_null")
        #cmds.parent(null, gp)
        poc = cmds.createNode("pointOnCurveInfo", name="middleZip"+str(i)+"_poc")
        cmds.setAttr(poc+".parameter", i)
        cmds.connectAttr("middleLipBase_crvShape.local", poc+".inputCurve")
        #cmds.connectAttr(poc+".position", null+".translate")
        
    for w in ["upper", "lower"]:
        for i in range(0,21):
            cmds.select(clear=1)
            #jnt = cmds.createNode("joint", name=w+"Zip"+str(i)+"_jnt")
            #cmds.setAttr(jnt+".radius", .2)
            #cmds.parent(jnt, gp)
            #createObjOffset(jnt)
            jnt = w+"Zip"+str(i)+"_jnt"
            poc = cmds.createNode("pointOnCurveInfo", name=w+"Zip"+str(i)+"_poc")
            cmds.setAttr(poc+".parameter", i)
            cmds.connectAttr(w+"LipBase_crvShape.local", poc+".inputCurve")
            #cmds.connectAttr(poc+".position", w+"Zip"+str(i)+"_jntOffset.translate")
    
            pma = cmds.createNode("plusMinusAverage", name=w+"Zip"+str(i)+"_pma")
            mlt = cmds.createNode("multiplyDivide", name=w+"Zip"+str(i)+"_mlt")
            cmds.setAttr(pma+".operation", 2)
            for axe in ["X","Y","Z"]:
                cmds.connectAttr("middleZip"+str(i)+"_poc.position"+axe, pma+".input3D[0].input3D"+axe.lower())
                cmds.connectAttr(w+"Zip"+str(i)+"_jntOffset.translate"+axe, pma+".input3D[1].input3D"+axe.lower())
                cmds.connectAttr(pma+".output3D"+axe.lower(), mlt+".input1"+axe)
                cmds.connectAttr("lipCorner_ctr_L.zip", mlt+".input2"+axe)
                cmds.connectAttr(mlt+".output"+axe, jnt+".translate"+axe)
            
createZipSystemAlone()

def createZipEase():
    for w in ["upper","lower"]:
        for side in ["_L", "_R"]:
            rev = cmds.createNode("reverse", n=w+"ZipEase_rev"+side)
            cmds.connectAttr("lipCorner_ctr"+side+".zipEase", rev+".inputX")
            
            
            for i in range(0, 21):
                mltEase = cmds.createNode("multiplyDivide", name=w+"ZipEase"+str(i)+"_mlt"+side)
                rng = cmds.createNode("setRange", name=w+"ZipEase"+str(i)+"_rng"+side)
                cmds.connectAttr("lipCorner_ctr"+side+".zip", rng+".valueX")
                cmds.setAttr(rng+".minX", 0)
                cmds.setAttr(rng+".maxX", 1)
                coef = i + 0.
                if side == "_R":
                    coef = 20. - i
                    
                cmds.setAttr(rng+".oldMaxX", (coef+1)*.5)
                cmds.setAttr(mltEase+".input2X", coef*.5)
                cmds.connectAttr(rev+".outputX", mltEase+".input1X")
                cmds.connectAttr(mltEase+".outputX", rng+".oldMinX")
                
        for i in range(0,21):
            mlt = w+"Zip"+str(i)+"_mlt"
            pma = cmds.createNode("plusMinusAverage", name=w+"ZipEase"+str(i)+"_pma")
            rngL = w+"ZipEase"+str(i)+"_rng_L"
            rngR = w+"ZipEase"+str(i)+"_rng_R"
            cmds.connectAttr(rngL+".outValueX", pma+".input1D[0]")
            cmds.connectAttr(rngR+".outValueX", pma+".input1D[1]")
            rng = cmds.createNode("setRange", name=w+"ZipEase"+str(i)+"_rng")
            cmds.connectAttr(pma+".output1D", rng+".valueX")
            cmds.setAttr(rng+".minX", 0)
            cmds.setAttr(rng+".maxX", 1)
            cmds.setAttr(rng+".oldMinX", 0)
            cmds.setAttr(rng+".oldMaxX", 1)
            for axe in ["X", "Y", "Z"]:
                cmds.disconnectAttr("lipCorner_ctr_L.zip", mlt+".input2"+axe)
                cmds.connectAttr(rng+".outValueX", mlt+".input2"+axe)
                
                
createZipEase()
                
                
def attachLipsCtrl():
    for side in ["_L", "_R"]:
        for w in ["upper", "lower"]:
            for l in ["Out", "Mid"]:
                param = 0
                if side == "_L":
                    if l == "Out":
                        param = 4
                    else:
                        param = 8
                else:
                    if l == "Out":
                        param = 16
                    else:
                        param = 12
                poc = cmds.createNode("pointOnCurveInfo", n=w+"Lip"+l+"Ctr_poc"+side)
                cmds.connectAttr(w+"LipDrv_crv.local", poc+".inputCurve")
                cmds.setAttr(poc+".parameter", param)
                cmds.connectAttr(poc+".position", w+"Lip"+l+"_ctrDriven"+side+".translate")
                
        poc = cmds.createNode("pointOnCurveInfo", n="lipCornerCtr_poc"+side)
        param = 0
        if side == "_R":
            param = 20
        cmds.connectAttr("upperLipDrv_crv.local", poc+".inputCurve")
        cmds.setAttr(poc+".parameter", param)
        cmds.connectAttr(poc+".position", "lipCorner_ctrDriven"+side+".translate")
        
attachLipsCtrl()
                
               
                
                
def createLipSecondary():
    for w in ["upper", "lower"]:
        for i in range(0,21):
            poc = cmds.createNode("pointOnCurveInfo", n = w+"LipCtr"+str(i)+"_poc")
            cmds.connectAttr(w+"LipCtr_crvShape.local", poc+".inputCurve")
            cmds.setAttr(poc+".parameter", i)
            pma = cmds.createNode("plusMinusAverage", n=w+"LipCtr"+str(i)+"_pma")
            cmds.setAttr(pma+".operation", 2)
            cmds.connectAttr(poc+".position", pma+".input3D[0]")
            for axe in ["X", "Y", "Z"]:
                cmds.setAttr(pma+".input3D[1].input3D"+axe.lower(), cmds.getAttr(poc+".position"+axe))
            createObjOffset(w+"Zip"+str(i)+"_jnt", nOff = "Driven")
            cmds.connectAttr(pma+".output3D", w+"Zip"+str(i)+"_jntDriven.translate")
            
            
createLipSecondary()
                
                
def createLipSecCtrl():
    for w in ["upper", "lower"]:
        for i in range (1,5):
            cmds.cluster(w+"LipCtrSpline_crv.cv["+str(i)+"]", n=w+"Lip"+str(i)+"_cls")
            cls = w+"Lip"+str(i)+"_clsHandle"
            cmds.parent(cls, "lipsCls_gp")
            if i == 1:
                cmds.connectAttr(w+"LipOut_ctr_L.translate", cls+".translate")
            elif i == 2:
                cmds.connectAttr(w+"LipMid_ctr_L.translate", cls+".translate")
            elif i == 3:
                cmds.connectAttr(w+"LipMid_ctr_R.translate", cls+".translate")
            elif i == 4:
                cmds.connectAttr(w+"LipOut_ctr_R.translate", cls+".translate")
                
createLipSecCtrl()
                
                
                
 def createSideShapes():
    sel = cmds.ls(sl=1)
    id = 1
    for obj in sel:
        for side in ["L", "R"]:
            cmds.blendShape("head_shape_"+side+"BS", e=1, t=("head_shape_"+side, id, obj, 1.0))
            cmds.setAttr("head_shape_"+side+"BS."+obj, 1)
            newShape = cmds.duplicate("head_shape_"+side, n=obj+"_"+side, st=1)
            cmds.parent(newShape, "baseShapes")
            cmds.setAttr("head_shape_"+side+"BS."+obj, 0)
        id += 1
                
                
                
createSideShapes()               




def connectLipShapes():
    for side in ["_L", "_R"]:
        dict = {"LipStretch":["X",[0,1,0,2]], "LipSquash":["X",[1,0,-2,0]], "Smile":["Y",[0,1,0,2]], "Sad":["Y",[1,0,-2,0]]}
        for elem in ["LipStretch", "LipSquash", "Smile", "Sad"]:
            rng = cmds.createNode("setRange", n=elem+"_rng"+side)
            cmds.setAttr(rng+".minX", dict[elem][1][0])
            cmds.setAttr(rng+".maxX", dict[elem][1][1])
            cmds.setAttr(rng+".oldMinX", dict[elem][1][2])
            cmds.setAttr(rng+".oldMaxX", dict[elem][1][3])
            cmds.connectAttr("lipCorner_ctr"+side+".translate"+dict[elem][0], rng+".valueX")
            cmds.connectAttr(rng+".outValueX","headLips_bds.head"+elem+"_tgt"+side)
            
            
connectLipShapes()

import maya.cmds as cmds

def createFinalZip():
    for w in ["lower", "upper"]:
        for i in range(0,21):
            pma = w+"Zip"+str(i)+"_pma"
            off = w+"Zip"+str(i)+"_jntOffset"
            drv = w+"Zip"+str(i)+"_jntDriven"
            
            pma2 = cmds.createNode("plusMinusAverage", name=w+"Zip"+str(i)+"Avg_pma")
            for axe in ["X","Y","Z"]:
                cmds.connectAttr(off+".translate"+axe, pma2+".input3D[0].input3D"+axe.lower())
                cmds.connectAttr(drv+".translate"+axe, pma2+".input3D[1].input3D"+axe.lower())
                cmds.disconnectAttr(off+".translate"+axe, pma+".input3D[1].input3D"+axe.lower())
                cmds.connectAttr(pma2+".output3D"+axe.lower(), pma+".input3D[1].input3D"+axe.lower())






import maya.cmds as cmds

def createMouthShapes():
    upDown = ["Inside", "Outside", "Outside25", "Outside50", "Inside50"]
    n0 = 0
    for side in ["U", "D"]: 
        for shp in upDown:
            shpName = "head"+shp+"_tgt"
            cmds.blendShape("head_shape_"+side+"BS", edit=1, t=("head_shape_"+side, n0, shpName, 1))
            cmds.setAttr("head_shape_"+side+"BS."+shpName, 1)
            new = cmds.duplicate("head_shape_"+side, n="head"+shp+side+"_tgt", st=1)[0]
            cmds.setAttr("head_shape_"+side+"BS."+shpName, 0)
            cmds.parent(new, "mouthShapes_gp_"+side)
            cmds.blendShape("head_shape_"+side+"BS", edit=1, rm=1, g=shpName)
            n0 += 1
        
    n = 0
    allShp = ["Smile", "Sad", "Crease", "Wide", "Narrow", "Puff", "Suck", "Sneer", "InsideU", "InsideD", "OutsideU", "OutsideD", 
    "Outside25D", "Outside50D", "Inside50D", "Outside25U", "Outside50U", "Inside50U"]
    id = {}
    
    for side in ["L", "R"]:
        for shp in allShp:
            bdsNode = "headLips_bds"
            bdsTgt = "headLips_tgt"
            if shp == "Sneer":
                bdsNode = "headNose_bds"
                bdsTgt = "headNose_tgt"
                
            shpName = "head"+shp+"_tgt"
            cmds.blendShape("head_shape_"+side+"BS", edit=1, t=("head_shape_"+side, n, shpName, 1))
            cmds.setAttr("head_shape_"+side+"BS."+shpName, 1)
            new = cmds.duplicate("head_shape_"+side, n=shpName+"_"+side, st=1)[0]
            cmds.setAttr("head_shape_"+side+"BS."+shpName, 0)
            cmds.parent(new, "mouthShapes_gp_"+side)
            cmds.blendShape("head_shape_"+side+"BS", edit=1, rm=1, g=shpName)
              
            if shp not in ["Outside25D", "Outside50D", "Inside50D", "Outside25U", "Outside50U", "Inside50U"]:
                cmds.blendShape(bdsNode, edit=1, t=(bdsTgt, n, new, 1))
                id[new] = n
                if cmds.objExists("head"+shp+"_rng_"+side):
                    rng = "head"+shp+"_rng_"+side
                    cmds.connectAttr(rng+".outValueX", bdsNode+"."+new)
            n+=1
        
        
    for shp in ["Inside"]:
        for sd in ["L", "R"]:
            for side in ["U", "D"]:
                cmds.blendShape("head_bds", e=1, ib=1, t=("headSquash_tgt", id["head"+shp+side+"_tgt_"+sd], "head"+shp+"50"+side+"_tgt_"+sd, .5))
                
    cmds.blendShape("headLips_bds", edit=1, t=("headLips_tgt", n, "headJaw_tgt", 1))
    cmds.connectAttr("headJaw_rng.outValueX", "headLips_bds.headJaw_tgt")
                
                
createMouthShapes()





import maya.cmds as cmds

def createMouthShapes2():
    allShp = ["Smile", "Sad", "Crease", "Wide", "Narrow", "Puff", "Suck", "Sneer", "InsideU", "InsideD", "UpperPush", "LowerPush", 
    "Inside50D", "Inside50U", "CheeksUp", "NeckTension", "EyebrowsIn", "EyebrowsDown", "UpperLidOpen", "LowerLidOpen", "LipUp", "CheeksLid"]
    
    for side in ["L", "R"]:
        n = 0
        n2 = 0
        for shp in allShp:
            bdS = side
            id = n
            if shp in ["InsideU", "Inside50U", "UpperPush","LowerPush", "Inside50D", "InsideD"]: 
                bdS = side+"S"
                id = n2
                
            shpName = "head"+shp+"_tgt"
            cmds.blendShape("head_shape_"+bdS+"BS", edit=1, t=("head_shape_"+bdS, id, shpName, 1))
            cmds.setAttr("head_shape_"+bdS+"BS."+shpName, 1)
            new = cmds.duplicate("head_shape_"+bdS, n=shpName+"_"+side, st=1)[0]
            cmds.setAttr("head_shape_"+bdS+"BS."+shpName, 0)
            cmds.parent(new, "mouthShapes_gp_"+side)
            cmds.blendShape("head_shape_"+bdS+"BS", edit=1, rm=1, g=shpName)
                    
            if bdS == side:
                n+=1
            else:
                n2+=1
        
                
createMouthShapes2()




def connectMouthShapes2():
    allShp = ["Smile", "Sad", "Crease", "Wide", "Narrow", "Puff", "Suck", "Sneer", "InsideU", "InsideD", "UpperPush", "LowerPush", 
    "CheeksUp", "NeckTension", "EyebrowsIn", "UpperLidOpen", "LowerLidOpen", "LipUp", "CheeksLid"]
    for side in ["L", "R"]:
        for shp in allShp:
            ax = "X"
            if side == "R":
                ax = "Y"
            
            bds = "head_bds"
            if shp == "LipUp":
                bds = "headLips_bds"
                   
            #cmds.connectAttr("head"+shp+"_rng.outValue"+ax, "head_bds.head"+shp+"_tgt_"+side)
            cmds.disconnectAttr("head"+shp+"_rng.outValue"+ax, bds+".head"+shp+"_tgt_"+side)
            
connectMouthShapes2()



def tongueEase():
    for i in range(1, 6):
        min = 1
        max = 0
        if i == 2:
            min = .75
            max = .25
        elif i == 3:
            min = .5
            max = .5
        elif i == 4:
            min = .25
            max = .75
        elif i == 5:
            min = 0
            max = 1
            
        rng = cmds.createNode("setRange", n="tongue0"+str(i)+"_rng")
        cmds.connectAttr("tongue_ctr.rollEase", rng+".valueX")
        cmds.connectAttr("tongue_ctr.rollEase", rng+".valueY")
        cmds.setAttr(rng+".oldMinX", -1)
        cmds.setAttr(rng+".oldMaxX", 1)
        cmds.setAttr(rng+".minX", min)
        cmds.setAttr(rng+".maxX", max)
        cmds.setAttr(rng+".oldMinY", -1)
        cmds.setAttr(rng+".oldMaxY", 1)
        cmds.setAttr(rng+".minY", min)
        cmds.setAttr(rng+".maxY", max)
        pma = cmds.createNode("plusMinusAverage", n="tongue0"+str(i)+"_pma")
        mlt = cmds.createNode("multiplyDivide", n="tongue0"+str(i)+"_mlt")
        cmds.connectAttr(rng+".outValueX", pma+".input1D[0]")
        cmds.connectAttr(rng+".outValueY", pma+".input1D[1]")
        cmds.connectAttr(pma+".output1D", mlt+".input1X")
        cmds.connectAttr("tongue_ctr.roll", mlt+".input2X")
        cmds.connectAttr(mlt+".outputX", "tongue0"+str(i)+"_skn_L.rotateX")
        cmds.connectAttr(mlt+".outputX", "tongue0"+str(i)+"_skn_R.rotateX")
        
tongueEase()


''' create lip Slide'''

rngGb = cmds.createNode("setRange", n="mouthMoveGb_rng")
cmds.connectAttr("locator1.translateX", rngGb+".valueX")
cmds.connectAttr("locator1.translateX", rngGb+".valueY")

cmds.setAttr(rngGb+".oldMinX", -7)
cmds.setAttr(rngGb+".oldMaxX", 7)
cmds.setAttr(rngGb+".minX", .1)
cmds.setAttr(rngGb+".maxX", .632)

cmds.setAttr(rngGb+".oldMinY", -7)
cmds.setAttr(rngGb+".oldMaxY", 7)
cmds.setAttr(rngGb+".minY", .366)
cmds.setAttr(rngGb+".maxY", .9)


for i in range(0,31):
    cmds.select(clear=1)
    jnt = cmds.createNode("joint", n="mouthMove"+str(i)+"_jnt")
    cmds.setAttr(jnt+".radius", .3)
    cmds.parent(jnt, "mouthMoveSetup_gp")
    poc = cmds.createNode("pointOnCurveInfo", n = "mouthMove"+str(i)+"_poc")
    cmds.setAttr(poc+".turnOnPercentage", 1)
    cmds.connectAttr("mouthMove_crv.local", poc+".inputCurve")
    coef = (1./30.)*float(i)
    cmds.setAttr(poc+".parameter", coef)
    cmds.connectAttr(poc+".position", jnt+".translate")
    if i >= 11 and i <= 19:
        rng = cmds.createNode("setRange", n = "mouthMove"+str(i)+"_rng")
        cmds.connectAttr("locator1.translateX", rng+".valueX")
        cmds.setAttr(rng+".oldMaxX", 7)
        cmds.setAttr(rng+".oldMinX", -7)
        cmds.setAttr(rng+".maxX", coef+.266)
        cmds.setAttr(rng+".minX", coef-.266)
        cmds.connectAttr(rng+".outValueX", poc+".parameter")
    elif i < 11:
        rng = cmds.createNode("setRange", n = "mouthMove"+str(i)+"_rng")
        cmds.setAttr(rng+".valueX", coef)
        cmds.setAttr(rng+".oldMaxX", .366)
        cmds.setAttr(rng+".oldMinX", 0)
        cmds.connectAttr(rngGb+".outValueX", rng+".maxX")
        cmds.setAttr(rng+".minX", 0)
        cmds.connectAttr(rng+".outValueX", poc+".parameter")
    elif i > 19:
        rng = cmds.createNode("setRange", n = "mouthMove"+str(i)+"_rng")
        cmds.setAttr(rng+".valueX", coef)
        cmds.setAttr(rng+".oldMaxX", 1)
        cmds.setAttr(rng+".oldMinX", .633)
        cmds.connectAttr(rngGb+".outValueY", rng+".minX")
        cmds.setAttr(rng+".maxX", 1)
        cmds.connectAttr(rng+".outValueX", poc+".parameter")














