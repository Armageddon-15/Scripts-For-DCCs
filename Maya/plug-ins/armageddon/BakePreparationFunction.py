# -*- coding: UTF-8 -*-

import core.ObjectTransformation as ObjTrans
import core.SelectionUtil as SelectUtils
import core.Utils as Utils
import core.Node as Node
import core.MayaWarning as MayaWarning

import pymel.core as core
import pymel.core.nodetypes as pmnt
import pymel.core.datatypes as pmdt 


def uniqueEachMaterial(include_children=False):
    sel = SelectUtils.orderedSeclect()
    transforms = []
    for obj in sel:
        if include_children:
            children = ObjTrans.getTransformAllChildren(obj, with_self=True)
            transforms.extend(children)
            
    print(transforms)
    for obj in transforms:
        if type(obj) is pmnt.Transform:
            # pmnt.ShadingEngine
            shape = ObjTrans.getTransformShapes(obj)[0]
        elif type(obj) is pmnt.Mesh:
            shape = obj
            
        name = obj.getName()
        print(name)
        
        dest_connect = core.listConnections(shape, c=True, d=True, s=False, type=pmnt.ShadingEngine)
        source_connect = core.listConnections(shape, c=True, s=True, d=False, p=True, type=pmnt.ShadingEngine)
        
        dest_conn_dict = {}
        for connection in dest_connect:
            attr = connection[0]
            if attr.find("compInstObjGroups") != -1:
                attr.disconnect()
                continue
            se = connection[1]
            if se in dest_conn_dict:
                dest_conn_dict[se].append(attr)
            else:
                dest_conn_dict.update({se:[attr]})
                
        source_conn_dict = {}
        for connection in source_connect:
            attr = connection[0]
            se, se_attr = connection[1].split(".", 1)
            se = pmnt.ShadingEngine(se)
            if se in source_conn_dict:
                source_conn_dict[se].append([attr, se_attr])
            else:
                source_conn_dict.update({se:[[attr, se_attr]]})
                
        # MayaWarning.information(dest_conn_dict.__str__)
        # MayaWarning.information(source_conn_dict.__str__)
        
        if not len(dest_conn_dict) > 0:
            continue
        
        shading_engines = dest_conn_dict.keys()
        
        with core.UndoChunk("unique materials"):
            # i = 0
            for e in shading_engines:
                # new_name = name + (str(i) if i>1 else "")
                new_name = name
                material = core.listConnections(e.surfaceShader)[0]
                if material.getName().find(name) != -1:
                    continue
                new_material = Node.copyNode(material)
                    
                new_material.setName(new_name)
                new_shading_engine = core.sets(renderable=1, noSurfaceShader=1, empty=1, name=new_name + "_SG")
                new_material.outColor.connect(new_shading_engine.surfaceShader)

                if e in source_conn_dict:
                    for attr_list in source_conn_dict[e]:
                        attr, se_attr = attr_list
                        attr.disconnect()
                        new_shading_engine.attr(se_attr).connect(attr)         
                            
                for attribute in dest_conn_dict[e]:
                    if type(attribute) is core.Attribute:
                        attribute.disconnect()
                        attribute.connect(new_shading_engine.dagSetMembers[0])
                        # core.sets(new_shading_engine, e=True, fe=attribute)
                # i += 1
            
            