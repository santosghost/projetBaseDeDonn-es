import argparse 
import sys
import svgwrite
import xml.etree.ElementTree as ET
import urllib
import json

parser = argparse.ArgumentParser(prog='XJ_convertor') # Syntaxe de la commande avec ses options

parser.add_argument('-i',dest='xml_json',choices=['xml','json'], help='Choix du type de fichier xml/json')
parser.add_argument('-t',dest='affichage',help='Affichage sur ecran de la liste des entites et des relations. Prend comme argument v pour dire affichage vrai')
parser.add_argument('-http',dest='flux_http',help='Permet de designer un flux http')
parser.add_argument('-f',dest='fichierInput',type=argparse.FileType('r'),help='Permet de designer un input de type fichier',default=sys.stdin)
parser.add_argument('-o',dest='fichierOutput',help='Permet de designer le fichier de sortie',default=sys.stdout)
args= parser.parse_args()


dwg = svgwrite.Drawing(args.fichierOutput,profile='tiny')       #Creation d'un fichier svg
dwg.viewbox(0,0,1900,800)
dwg.add(dwg.rect((0,0),size=('900%','500%'),fill="white",opacity='0.8'))

if args.flux_http :
	hres = urllib.request.urlopen(args.flux_http)  #Si le fichier est dans un serveur http

	fichier=hres.read()
else:
	fichier = args.fichierInput

def inserer_prop(str,s,xx,yy):									#insertion des proprietes
		y=yy
		for i in range(0,s):
			dwg.add(dwg.text(str[i],insert=(xx+10,yy+20),font_size=30))
			yy=yy+50
		dwg.add(dwg.rect(insert=(xx,y),size=("12%",yy-20),stroke='blue',fill='none'))
		return


def inserer_entite(str,tableauASSO,u,x,y):          #insertion des entites
		zz=[]
		tt=[]
		s=[x,x+1500]
		n=2
		d=[y,y,y+260,y+260,y+2*260,y+2*260]
		pp=[x+770,x+970]
		mm=[x+228,x+1500]
		uu=[x+280,x+1480]
		for i in range(0,u):
			t=n%2
			h=4*d[i]
			dwg.add(dwg.rect(insert=(s[t],d[i]),size=('12%','5%'),fill="none",stroke="blue"))
			dwg.add(dwg.text(str[i],insert=(s[t]+10,d[i]+30),stroke='black',font_size=30))
			if args.xml_json=='xml':
				tt=get_prop("entite",str[i],zz)	
			else:
				tt=obtenir_element("entite")
			inserer_prop(tt,len(tt),s[t],d[i]+75)	
			for j in tableauASSO:	
				if args.xml_json=='xml':
					if get_attrib_ass(j,str[i],"role"):
						role1=get_attrib_ass(j,str[i],"role")
						cardminmax=get_attrib_ass(j,str[i],"cardmin")+" , "+get_attrib_ass(j,str[i],"cardmax")
						dwg.add(dwg.line((pp[t],h),(mm[t],d[i]+50),stroke='black'))
						dwg.add(dwg.text(role1,(uu[t],h-45),fill='red',font_size=25,text_anchor='end'))
						dwg.add(dwg.text(cardminmax,(uu[t],d[i]+70),fill="green",font_size="20",text_anchor="end"),)
		
				if args.xml_json=='json':		
					for y in propriete_ass:
						if obtenir_attribut_ass(j,y,"ida")==str[i]:
							role=obtenir_attribut_ass(j,y,"role")
							cardminmax="("+obtenir_attribut_ass(j,y,"cardmin")+" , "+obtenir_attribut_ass(j,y,"cardmax")+")"
							dwg.add(dwg.line((pp[t],h),(mm[t],d[i]+50),stroke='black'))
							dwg.add(dwg.text(role,(uu[t],h-40),fill='red',font_size=25,text_anchor='end'))
							dwg.add(dwg.text(cardminmax,(uu[t],d[i]+70),fill="green",font_size="20",text_anchor="end"),)
			n=n+1	
			

		for i in range(0,len(tableauASSO)):    #insertion des associations
			dwg.add(dwg.ellipse(center=(x+870,h),r=(100,50),fill='black',opacity='0.7'))
			dwg.add(dwg.text(tableauASSO[i],insert=(x+860,h-30),fill='red',font_size=50,text_anchor='start'))

			if args.xml_json=="xml":
				t=get_prop("association",tableauASSO[i],zz)
				
			else:
				t=obtenir_prop("association")	
			yo=h-5	
			for j in range(0,len(t)):
				dwg.add(dwg.text(t[j],insert=(x+850,yo),fill='white',font_size=25,text_anchor='start'))		
	 	   	h=h+220	
		
		return


if args.xml_json=='xml': 			#Convertir un fichier xml un format SVG 
	print("xml choisi")	
	tree=ET.parse(fichier)
	entites= []
	association=[]
	prop_entite= []
	prop_ass=[]
	root=tree.getroot()

	def get_element(str,l):
		for child in root.iter(tag=str):
			 l.append(child.get("id"))
		return l

	def get_prop(p,str,l):
		l=[]
		for element in root.iter(tag=p):
			if((element.get("id"))==str):
				for child in element.iter(tag="propriete"):
					if((child.get("cle"))=="oui"):
						l.append(child.text+"--> cle")
					else:
						l.append(child.text)
		return l

	def get_attrib_ass(identifiantAsso,entite,attribut):
		for element in root.iter(tag="association"):
			if((element.get("id"))==identifiantAsso):
				for child in element.iter(tag="entasso"):
					if child.get("source")==entite:
						return 	child.get(attribut)


	get_element("entite",entites)
	get_element("association",association)
			
	inserer_entite(entites,association,len(entites),60,30)

	dwg.save()

if args.affichage=='v' and args.xml_json=="xml" :  #choix pour montrer sur au niveau ecran les entites et relations
	print("voici la liste des entites :",entites)
	print("Voici la liste des relations :",association)

if args.xml_json=="json": #Si le fichier est un fichier JSON

	fichier=args.fichierInput
	dict=json.load(fichier)  # Ce module en fait la validation
	
	def obtenir_element(str):
		l=[]
		for element in dict:
			if element.startswith(str):			
				l.append(element)
		return l

	def obtenir_prop(str):
		l=[]
		for element in dict:
			if element.startswith(str):
				for child in dict[element]:
					l.append(child)
		return l

	def obtenir_attribut(entite,nomprop,attribut):
		t=dict.get(entite)
		d=t.get(nomprop)
		z=d.get(attribut)
		return z

	def obtenir_attribut_ass(association,entite,attribut):
		z=dict.get(association)
		r=z.get(entite)
		e=r.get(attribut)
		return e
	entites_json=obtenir_element("entite")
	association_json=obtenir_element("association")
	propriete_ass=obtenir_prop("association")
	
	inserer_entite(entites_json,association_json,len(entites_json),60,15)

if args.affichage=='v' and args.xml_json=='json':
	print("Voici les entites du fichier json :",entites_json)
	print("Les relations associes:",association_json)

dwg.save()