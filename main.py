from kivy.app import App
from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label
from kivy.uix.togglebutton import ToggleButton
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.slider import Slider
from kivy.uix.button import Button
from kivy.uix.popup import Popup
from kivy.clock import Clock
from kivy.core.audio import SoundLoader
import random

class MyApp(App):
    def build(self):
        self.selected_buttons = []  # Liste pour stocker les boutons sélectionnés
        self.number_of_hits = 0  # Nombre de coups choisis

        # Dictionnaire associant chaque bouton à sa valeur
        self.button_values = {
            "Bouton 1": 1,
            "Bouton 2": 2,
            "Bouton 3": 3,
            "Bouton 4": 4,
            "Bouton 5": 5,
            "Bouton 6": 6
        }

        self.sounds = {
            1: SoundLoader.load('son1.mp3'),
            2: SoundLoader.load('son2.mp3'),
            3: SoundLoader.load('son3.mp3'),
            4: SoundLoader.load('son4.mp3'),
            5: SoundLoader.load('son5.mp3'),
            6: SoundLoader.load('son6.mp3')
        }

        # Layout principal (vertical) pour le titre, les boutons, slider et bouton de validation
        main_layout = BoxLayout(orientation='vertical', padding=10, spacing=10)

        # Ajout du titre
        title = Label(
            text="Quelle coup voulez-vous entraîner ?",  # Texte du titre
            font_size=24,
            size_hint=(1, 0.1)  # Ajuster la hauteur du titre
        )
        main_layout.add_widget(title)

        # Layout des boutons (grille avec 2 colonnes)
        button_layout = GridLayout(cols=2, padding=10, spacing=10)

        # Ajout de 6 ToggleButtons
        for i in range(1, 7):
            toggle = ToggleButton(
                text=f"Bouton {i}\nOFF",  # Texte initial avec état OFF
                state="normal",  # État initial
                background_color=(1, 0.3, 0.3, 1),  # Couleur rouge par défaut
                font_size=16
            )
            toggle.bind(on_press=self.on_toggle)  # Lier une fonction au clic
            button_layout.add_widget(toggle)

        # Ajouter le layout des boutons au layout principal
        main_layout.add_widget(button_layout)

        # Ajout du slider pour définir la durée de l'entraînement
        slider_layout = BoxLayout(orientation='vertical', spacing=10, size_hint=(1, 0.2))
        
        slider_label = Label(
            text="Durée de l'entraînement : 0 sec",
            font_size=18
        )
        self.slider = Slider(
            min=0,
            max=300,
            step=10,
            value=0
        )
        self.slider.bind(value=lambda instance, value: self.on_slider_value_change(instance, value, slider_label))

        slider_layout.add_widget(slider_label)
        slider_layout.add_widget(self.slider)
        main_layout.add_widget(slider_layout)

        # Ajout du deuxième slider pour le nombre de coups
        self.hit_slider_label = Label(
            text="Nombre de coups : 0",
            font_size=18
        )
        self.hit_slider = Slider(
            min=0,
            max=0,  # Initialement la valeur max est 0
            step=1,
            value=0
        )
        self.hit_slider.bind(value=self.on_hit_slider_value_change)

        hit_slider_layout = BoxLayout(orientation='vertical', spacing=10, size_hint=(1, 0.2))
        hit_slider_layout.add_widget(self.hit_slider_label)
        hit_slider_layout.add_widget(self.hit_slider)
        main_layout.add_widget(hit_slider_layout)

        # Ajout du bouton de validation centré en bas
        validate_button = Button(
            text="Valider",  # Texte du bouton
            size_hint=(0.5, 0.1),  # Taille ajustée
            pos_hint={'center_x': 0.5}  # Centré horizontalement
        )
        validate_button.bind(on_press=self.on_validate)  # Lier une fonction au clic
        main_layout.add_widget(validate_button)

        return main_layout

    def on_toggle(self, instance):
        # Basculer entre ON et OFF tout en gardant le nom du bouton
        button_number = instance.text.split("\n")[0]  # Récupérer le nom (Bouton X)
        if instance.state == "down":
            instance.text = f"{button_number}\nON"
            instance.background_color = (0.3, 1, 0.3, 1)  # Couleur verte
            self.selected_buttons.append(button_number)  # Ajouter le bouton sélectionné
        else:
            instance.text = f"{button_number}\nOFF"
            instance.background_color = (1, 0.3, 0.3, 1)  # Couleur rouge
            self.selected_buttons.remove(button_number)  # Retirer le bouton sélectionné

    def on_slider_value_change(self, instance, value, label):
        # Met à jour le texte de l'étiquette associée au slider
        value = int(value)  # Convertir la valeur en entier
        if value < 60:
            label.text = f"Durée de l'entraînement : {value} sec"
        else:
            minutes = value // 60
            seconds = value % 60
            label.text = f"Durée de l'entraînement : {minutes} min {seconds} sec"

        # Mettre à jour la valeur max du second slider en fonction du premier
        self.hit_slider.max = value
        self.hit_slider.value = min(self.hit_slider.value, value)  # Limiter la valeur du deuxième slider à la valeur du premier

    def on_hit_slider_value_change(self, instance, value):
        # Mise à jour de l'étiquette du nombre de coups
        self.hit_slider_label.text = f"Nombre de coups : {int(value)}"
        self.number_of_hits = int(value)

    def on_validate(self, instance):
        # Créer et afficher la fenêtre du chrono
        duration = int(self.slider.value)  # Durée en secondes
        self.create_hit_array(duration)  # Créer le tableau de coups basé sur la durée (nombre de secondes)
        self.calculate_time_left_after_hits(duration)  # Calculer la différence
        self.set_random_zeroes()  # Mettre à zéro les éléments du tableau de manière aléatoire
        self.popup_window(duration)

    def create_hit_array(self, duration):
    # Créer un tableau de taille 'duration' avec les valeurs des boutons sélectionnés
        if self.selected_buttons:
            # Le tableau sera de la taille 'duration' et contiendra des valeurs tirées des boutons sélectionnés
            self.hit_array = [self.button_values[button] for button in random.choices(self.selected_buttons, k=duration)]
        else:
            self.hit_array = []  # Si aucun bouton n'est sélectionné, tableau vide
        print(f"Tableau des coups : {self.hit_array}")  # Afficher le tableau dans la console


    def calculate_time_left_after_hits(self, duration):
        # Calculer la différence entre le nombre de secondes et le nombre de coups
        self.time_left_after_hits = duration - self.number_of_hits
        print(f"Temps restant après les coups : {self.time_left_after_hits} secondes")

    def set_random_zeroes(self):
        # Mettre à zéro des éléments aléatoires du tableau en fonction de 'time_left_after_hits'
        if self.time_left_after_hits > 0 and self.hit_array:
            # Sélectionner des indices aléatoires et les mettre à zéro
            indices_to_zero = random.sample(range(len(self.hit_array)), min(self.time_left_after_hits, len(self.hit_array)))
            for idx in indices_to_zero:
                self.hit_array[idx] = 0
        print(f"Tableau après modification : {self.hit_array}")

    def popup_window(self, duration):
        # Fenêtre pop-up avec le chrono
        self.popup_content = BoxLayout(orientation='vertical', padding=20, spacing=10)
        
        # Affichage des coups sélectionnés
        selected_label = Label(
            text="Coups sélectionnés :\n" + "\n".join(self.selected_buttons),
            font_size=18,
            size_hint=(1, 0.1)
        )
        self.popup_content.add_widget(selected_label)

        # Chrono au centre
        self.chrono_label = Label(
            text=f"{duration} sec",  # Temps initial
            font_size=50,
            size_hint=(1, 0.2),
            color=(1, 1, 1, 1)
        )
        self.popup_content.add_widget(self.chrono_label)

        # Affichage du nombre de coups
        hits_label = Label(
            text=f"Nombre de coups : {self.number_of_hits}",
            font_size=18,
            size_hint=(1, 0.1)
        )
        self.popup_content.add_widget(hits_label)

        # Affichage du tableau des coups
        hits_array_label = Label(
            text=f"Tableau des coups : {self.hit_array}",
            font_size=18,
            size_hint=(1, 0.1)
        )
        self.popup_content.add_widget(hits_array_label)

        self.popup = Popup(
            title="Entraînement",
            content=self.popup_content,
            size_hint=(0.8, 0.8)
        )
        self.popup.open()

        # Initialisation du temps restant
        self.time_left = duration
        self.last_sound_time = 0  # Temps du dernier son joué
        self.max_interval = 10  # Intervalle minimum entre 2 sons
        self.sound = SoundLoader.load('son1.mp3')  # Charger un son (remplacez par votre fichier)
        self.next_sound_time = random.randint(1, self.max_interval)  # Premier intervalle aléatoire entre 1 et 10 secondes
        Clock.schedule_interval(self.update_chrono, 1)  # Mettre à jour chaque seconde

    def play_random_sound(self):
        # Vérifier la valeur de la case du tableau et jouer le son correspondant
        if self.time_left < len(self.hit_array):
            hit_value = self.hit_array[self.time_left]  # Récupérer la valeur de la case actuelle
            sound = self.sounds.get(hit_value)  # Obtenir le son correspondant à la valeur
            
            if sound:
                sound.play()  # Jouer le son

    def update_chrono(self, dt):
        # Mettre à jour le chrono
        if self.time_left > 0:
            self.time_left -= 1
            
            # Vérifier la case du tableau correspondante
            if self.time_left < len(self.hit_array) and self.hit_array[self.time_left] != 0:
                self.play_random_sound()  # Si la case n'est pas zéro, jouer le son

            # Mise à jour de l'affichage
            if self.time_left < 60:
                self.chrono_label.text = f"{self.time_left} sec"
            else:
                minutes = self.time_left // 60
                seconds = self.time_left % 60
                self.chrono_label.text = f"{minutes} min {seconds} sec"
        else:
            # Lorsque le chrono atteint 0, arrêter l'intervalle
            Clock.unschedule(self.update_chrono)
            self.popup.dismiss()  # Fermer la fenêtre


if __name__ == '__main__':
    MyApp().run()
