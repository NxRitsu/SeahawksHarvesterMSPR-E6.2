import os
import tkinter as tk
from tkinter import ttk, scrolledtext
from ping3 import ping
import nmap
import psutil
from datetime import datetime
import xml.etree.ElementTree as ET

class ApplicationReseauAvecNmap:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Informations Réseau LAN")

        style = ttk.Style()
        style.theme_use("clam")

        self.root.geometry("800x600")

        self.label_ip = ttk.Label(self.root, text="Adresse IP LAN:")
        self.label_ip.pack(pady=10)

        self.nom_interface_lan = 'Wi-Fi'  # Changer en fonction de l'interface réseau utilisée sur Windows

        self.bouton_scan = ttk.Button(self.root, text="Scanner le Réseau", command=self.scanner_reseau)
        self.bouton_scan.pack(pady=10)

        self.frame_resultats = ttk.Frame(self.root)
        self.frame_resultats.pack(pady=10)

        self.label_resultats = scrolledtext.ScrolledText(self.frame_resultats, wrap=tk.WORD, width=60, height=15)
        self.label_resultats.pack()

        self.label_latence = ttk.Label(self.root, text="")
        self.label_latence.pack(pady=10)

        self.mise_a_jour_ip()
        self.afficher_dernier_scan()

        self.root.mainloop()

    def mise_a_jour_ip(self):
        adresse_ip = self.obtenir_ip_locale_lan()
        self.label_ip.config(text=f"Adresse IP LAN : {adresse_ip}")
        self.root.after(1000, self.mise_a_jour_ip)

    def obtenir_ip_locale_lan(self):
        try:
            adresse_ip = psutil.net_if_addrs()[self.nom_interface_lan][1].address  # Changer l'index selon l'interface
            return adresse_ip
        except Exception as e:
            print(f"Erreur lors de la récupération de l'adresse IP de la carte réseau LAN : {e}")
            return self.obtenir_ip_locale()

    def obtenir_ip_locale(self):
        try:
            adresse_ip = os.popen('ipconfig | findstr IPv4').read().split(':')[-1].strip()  # Utiliser ipconfig sur Windows
            return adresse_ip
        except Exception as e:
            print(f"Erreur lors de la récupération de l'adresse IP : {e}")
            return "N/A"

    def scanner_reseau(self):
        self.label_resultats.delete("1.0", tk.END)
        nm = nmap.PortScanner()
        nm.scan(hosts=f'{self.obtenir_ip_locale_lan()}/24', arguments='-p 1-1000')
        machines_connectees = len(nm.all_hosts())
        ports_ouverts = {}

        for machine in nm.all_hosts():
            ports_ouverts[machine] = []
            for proto in nm[machine].all_protocols():
                ports = nm[machine][proto].keys()
                ports_ouverts[machine].extend([(port, proto) for port in ports])

        texte_resultats = f"Machines Connectées : {machines_connectees}\n"
        for machine, ports in ports_ouverts.items():
            texte_resultats += f"\n{machine} - Ports Ouverts :\n"
            for port, proto in ports:
                texte_resultats += f"    {port}/{proto}\n"

        self.label_resultats.insert(tk.END, texte_resultats)

        latence = self.obtenir_latence_wan_ping3()
        self.label_latence.config(text=f"Latence WAN : {latence}")

        chemin_fichier_local = "resultats_scan.xml"
        self.sauvegarder_resultats_scan_xml(machines_connectees, ports_ouverts, latence)
        self.sauvegarder_resultats_scan_txt(machines_connectees, ports_ouverts, latence)

        self.transfere_resultats_scan_via_sftp(chemin_fichier_local)

    def obtenir_latence_wan_ping3(self):
        cible_ping = 'www.google.com'
        try:
            latence = ping(cible_ping, unit='ms')
            return f"{latence:.2f} ms" if latence is not None else "N/A"
        except Exception as e:
            print(f"Erreur lors de la mesure de la latence WAN avec Ping3 : {e}")
            return "N/A"

    def sauvegarder_resultats_scan_xml(self, machines_connectees, ports_ouverts, latence):
        horodatage = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        racine = ET.Element("harvester_info")
        ET.SubElement(racine, "ip_address").text = self.obtenir_ip_locale_lan()
        ET.SubElement(racine, "connected_machines").text = str(machines_connectees)

        last_scan_element = ET.SubElement(racine, "last_scan")
        ET.SubElement(last_scan_element, "timestamp").text = horodatage

        results_element = ET.SubElement(last_scan_element, "results")
        for machine, ports in ports_ouverts.items():
            machine_element = ET.SubElement(results_element, "machine")
            ET.SubElement(machine_element, "name").text = machine
            ET.SubElement(machine_element, "ip").text = machine
            open_ports_element = ET.SubElement(machine_element, "open_ports")
            for port, proto in ports:
                ET.SubElement(open_ports_element, "port").text = f"{port}/{proto}"

        ET.SubElement(racine, "wan_latency").text = latence

        tree = ET.ElementTree(racine)
        tree.write("resultats_scan.xml")

    def sauvegarder_resultats_scan_txt(self, machines_connectees, ports_ouverts, latence):
        horodatage = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        with open("resultats_scan.txt", "w") as fichier:
            fichier.write(f"Horodatage : {horodatage}\n")
            fichier.write(f"Machines Connectées : {machines_connectees}\n")
            for machine, ports in ports_ouverts.items():
                fichier.write(f"\n{machine} - Ports Ouverts :\n")
                for port, proto in ports:
                    fichier.write(f"    {port}/{proto}\n")
            fichier.write(f"Latence WAN : {latence}\n")

    def transfere_resultats_scan_via_sftp(self, chemin_fichier_local):
        adresse_du_nester = "192.168.1.88"
        nom_utilisateur = "melvin"
        chemin_distant = "/home/melvin/Nester/path_to_xml_files/1.xml"

        with pysftp.Connection(adresse_du_nester, username=nom_utilisateur) as sftp:
            sftp.put(chemin_fichier_local, chemin_distant)

        print(f"Fichier XML envoyé avec succès via SFTP vers {chemin_distant}")

    def afficher_dernier_scan(self):
        try:
            with open("resultats_scan.txt", "r") as fichier:
                dernier_scan = fichier.read()

            # Détruire le widget précédent
            self.label_resultats.delete("1.0", tk.END)

            self.label_resultats.insert(tk.END, dernier_scan)
        except FileNotFoundError:
            self.label_resultats.insert(tk.END, "Aucun résultat de scan précédent trouvé.")

# Instancier l'application
app_reseau = ApplicationReseauAvecNmap()
