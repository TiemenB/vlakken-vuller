# Dit is voor het vullen van polygons zonder vlak. 
# Het werkt alleen in 2D vlak
# Er wordt gekeken naar de omtrek van ieder vlak, binnen het vlak zitten geen lijnen
# eerste een lijn selecteren aan de buitenrand


import mathutils
from mathutils import Vector
import bmesh
import bpy
from math import pi,degrees
print('xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx')


# geeft het lijnstuk terug dat de kleinste hoek maakt met het binnen komende lijnstuk

def kleinste_klokmee_hoek(bm, startlijn,startpunt):
    eindpunt = startlijn.other_vert(startpunt)
    
    aanliggen_lijnen = list(eindpunt.link_edges)

    aanliggen_lijnen.remove(startlijn)

    vectoren = []
    for l in aanliggen_lijnen:
        punt2 = l.other_vert(eindpunt)
        vect = eindpunt.co - punt2.co
        vect.resize_2d()
        vectoren.append(vect)
        
    start_vector = eindpunt.co - startpunt.co  
    start_vector.resize_2d()
    kleinste = 400
    for t,v in enumerate(vectoren):
        h = start_vector.angle_signed(v)
        
        if h < 0:
            h = 2 *pi+h
        if h == 0:
            
            h = pi
        if h<kleinste:
            kleinste = h
            nummer = t
        
  
    return(aanliggen_lijnen[nummer])

# wordt niet gebruit, bedoeld om een randstuk te vinden
def rand_lijn(bm):
    kleinste = 100000
    for p in bm.verts:
        if p.select:
            if p.co[0] < kleinste:
                kleinste = p.co[0]
                kleinste_p = p 
    print(kleinste_p.index)            
    buiten_lijn = kleinste_p.link_edges[0]
    bpy.ops.mesh.select_all(action='DESELECT')

    return(buiten_lijn)

# selecteert de omtrek via steeds de kleinste hoek in een richting    
def omtrek(bm,startlijn,richting):
    startpunt = startlijn.verts[richting]
    eerste_punt = startpunt
    eindpunt = startlijn.other_vert(startpunt)
    doorgaan = True
    teller = 0
    alle_lijnen =[startlijn]
    while doorgaan:
        teller +=1
        if len(eindpunt.link_edges)>2:
            nieuwe_lijn = kleinste_klokmee_hoek(bm,startlijn,startpunt)
            #print('groter dan twee')
        else:
            alle = list(eindpunt.link_edges)
            alle.remove(startlijn)
            nieuwe_lijn = alle[0]
        startpunt = eindpunt
        nieuw_punt = nieuwe_lijn.other_vert(eindpunt)
        nieuwe_lijn.select_set(True)
        startlijn = nieuwe_lijn
        alle_lijnen.append(nieuwe_lijn)
        eindpunt = nieuw_punt
        
        
        if teller > 10000:
            doorgaan = False
        if eindpunt == eerste_punt:
            doorgaan = False
            print('Ik was klaar hoor')
    
        
    bmesh.update_edit_mesh(me, loop_triangles=True) 
    return(alle_lijnen)

def alle_lijnen_func(bm):
    bpy.ops.mesh.select_linked()
    alle_lijnen = []
    for l in bm.edges:
        if l.select:
            alle_lijnen.append(l)
    bpy.ops.mesh.select_all(action='DESELECT')

    return(alle_lijnen)

def lijst_opschonen(alle,weghalen): 
    alle_set= set(alle)
    weghalen_set = set(weghalen)
    over = alle_set - weghalen_set
    over = list(over) 
    return(over) 
         
# gaat vanuit de startlijn(die op de buitenkant moet liggen)twee omtrekken bepalen,links om en rechts om.
# Daarna wordt van bijde het opeervlakte berekend. Het grootste oppervlak hoort bij de 
# hele figuur. Er wordt een lijst terug gegeven van de lijnen de omtrek
 
def bepaal_omtrek(bm,startlijn):
    richting = 0
    alle_lijnen_0 = omtrek(bm,startlijn,richting) 
    bpy.ops.mesh.edge_face_add()
    for f in bm.faces:
        opperv_0 =  f.calc_area()  
        #print(f'oppervlak 1:{a}')

    bpy.ops.mesh.delete(type='ONLY_FACE')
     
     
    richting = 1 
    alle_lijnen_1 = omtrek(bm,startlijn,richting)   
    bpy.ops.mesh.edge_face_add()
    for f in bm.faces:
        opperv_1 =  f.calc_area()  
        #print(f'oppervlak 2:{a}')
    bpy.ops.mesh.delete(type='ONLY_FACE')

    if opperv_0 > opperv_1:
        omtrek_buiten = alle_lijnen_0
        richting = 0
    else:
        omtrek_buiten = alle_lijnen_1
        richting = 1
    return(omtrek_buiten)

# vanuit een binnenlijn wordt een gesloten oppervlak bepaald, daarna worden de gebruikte lijken van het totaal van binnenlijnen
# afgetrokken. Met de rest wordt doorgegaan tot er niets over is.
# Er blijven daarna nog gaten tussen de vlakken zitten.

def vullen_in_richting(bm,richting,binnen_lijnen):
    doorgaan = True
    teller = 0
    
    print(f'lengte is:{len(alle_lijnen)}')
    
    

    while doorgaan:
        
        teller += 1 
        
        
        if len(binnen_lijnen) <1:
            break
        omtrek_buiten = omtrek(bm,binnen_lijnen[0],richting)
        binnen_lijnen = lijst_opschonen(binnen_lijnen,omtrek_buiten)
        bpy.ops.mesh.edge_face_add()
        bpy.ops.mesh.select_all(action='DESELECT')
        print(f'lengte alle lijnen:{len(alle_lijnen)}')
        
        if teller >10000:
            doorgaan = False
            
# de vlakken die over zijn gebleven en eerder niet gevuld werden, worden hier opgezocht en gevuld 
   
def niet_gevuld(bm,binnen_lijnen):
    for e in binnen_lijnen:
        if len(e.link_faces) == 1:
            richting = 1
            omt = omtrek(bm,e,richting)
            print(f'inhoud omtrek:{len(omt)}')
            for l in omt:
                if len(l.link_faces) >1 :
                    bpy.ops.mesh.select_all(action='DESELECT')
                    richting = 0
                    omt = omtrek(bm,e,richting)
                    
            bpy.ops.mesh.edge_face_add()
            bpy.ops.mesh.select_all(action='DESELECT')
            bmesh.update_edit_mesh(me, loop_triangles=True)  
            
        
             
        
####################### programma ############################   

ob = bpy.context.object
me = ob.data
bm = bmesh.from_edit_mesh(me)

#startlijn = rand_lijn(bm)

for l in bm.edges:
    if l.select:
        startlijn = l
        break
    
# lijst maken van alle lijnen     
alle_lijnen = alle_lijnen_func(bm)

alle_lijnen_res = alle_lijnen
    


omtrek_buiten = bepaal_omtrek(bm,startlijn)
#for l in omtrek_buiten:
#    l.select_set(True)
binnen_lijnen = lijst_opschonen(alle_lijnen,omtrek_buiten)

#for l in binnen_lijnen:
#    l.select_set(True)

richting = 0
vullen_in_richting(bm,richting,binnen_lijnen)
'''
richting = 1
vullen_in_richting(bm,richting,binnen_lijnen)
'''

niet_gevuld(bm,binnen_lijnen)
bpy.ops.mesh.select_all(action='SELECT')
bpy.ops.mesh.normals_make_consistent(inside=False)












   
bmesh.update_edit_mesh(me, loop_triangles=True)  


    
