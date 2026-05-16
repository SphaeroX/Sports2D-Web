# Machbarkeitsstudie: Körperanalyse für Bike-Fitting mittels Sports2D

## 1. Einleitung
Diese Machbarkeitsstudie untersucht, ob es möglich ist, anhand von einfachen Video- oder Fotoaufnahmen einer Person und der Eingabe der Gesamtkörpergröße eine Körperanalyse für das **Bike-Fitting** durchzuführen. Als technologische Grundlage wird **Sports2D** (bzw. die zugrundeliegenden Modelle wie RTMPose/HALPE_26) evaluiert. Das Ziel ist es, fahrradrelevante Maße wie die Schrittlänge, Rumpflänge, Armlänge und Schulterbreite aus den Bildern auszulesen.

## 2. Technologische Basis: Sports2D
Sports2D ist ein Open-Source-Tool für markerlose 2D-Kinematik (Pose Estimation). Es erkennt in Videos (oder Webcam-Streams) automatisch menschliche Gelenkpunkte (Keypoints).
Standardmäßig verwendet Sports2D ein Modell, das 26 Körper-Keypoints (z.B. HALPE_26) erfasst. Darunter befinden sich für unser Vorhaben alle relevanten Gelenke:
- Kopf/Gesicht (Nose, Head, Neck)
- Schultern (L/R Shoulder)
- Arme (L/R Elbow, L/R Wrist)
- Hüfte (L/R Hip, Center Hip)
- Beine (L/R Knee, L/R Ankle, L/R Heel, L/R Big/Small Toe)

Die Erkennung dieser Gelenkpunkte in einem Bild liefert (x, y)-Koordinaten in Pixeln.

## 3. Methodik der Längenbestimmung

Um von reinen Pixel-Koordinaten zu realen Längen (in cm) zu gelangen, ist eine Skalierung notwendig. Dies geschieht anhand der **bekannten Gesamtkörpergröße**.

### 3.1 Skalierung (Pixel zu cm)
Es wird vorausgesetzt, dass die Person in mindestens einem Frame des Videos aufrecht und gerade steht.
In diesem Moment wird die maximale Ausdehnung der Person in Pixeln gemessen:
- **Oberer Punkt:** Der `Head`-Keypoint (oder der obere Rand der Bounding-Box/Kopfkontur, da "Head" oft auf Scheitelhöhe oder Nasenwurzel sitzt, muss ggf. durch einen Offset korrigiert werden).
- **Unterer Punkt:** Der tiefste Punkt der Füße (Durchschnitt der y-Koordinaten von `RHeel` und `LHeel` oder `RBigToe/LBigToe`).

Die Distanz zwischen diesen beiden Punkten entspricht der Körpergröße in Pixeln ($H_{px}$).
Der Umrechnungsfaktor ($S$) ergibt sich aus der vom Nutzer eingegebenen echten Körpergröße ($H_{cm}$):

$$S = \frac{H_{cm}}{H_{px}} \quad \text{[(cm) / Pixel]}$$

### 3.2 Berechnung der fahrradspezifischen Maße
Nachdem der Faktor $S$ berechnet wurde, können beliebige Segmentlängen im Bild in reale Maße umgerechnet werden.
Die Berechnung erfolgt über den **Euklidischen Abstand** ($d = \sqrt{(x_2 - x_1)^2 + (y_2 - y_1)^2}$) oder rein vertikale/horizontale Abstände.

1. **Schrittlänge (Innenbeinlänge)**
   - Wichtigstes Maß für die Bestimmung der Rahmenhöhe und Sattelhöhe.
   - **Realisierung:** Die vertikale Distanz zwischen dem Mittelpunkt der Hüftgelenke (`Hip`) und dem Boden (Fersen `Heel`). Alternativ die Summe der Segmente: Distanz(Hip, Knee) + Distanz(Knee, Ankle) + Distanz(Ankle, Heel).
2. **Rumpflänge**
   - Wichtig für die Oberrohrlänge und die Sitzhaltung (Reach).
   - **Realisierung:** Distanz vom Zentrum der Schultern (`Neck` oder Mitte zwischen `LShoulder` und `RShoulder`) zum Zentrum der Hüfte (`Hip`).
3. **Armlänge**
   - Relevant für den Reach und den Vorbau.
   - **Realisierung:** Summe aus Oberarm- und Unterarmlänge.
   - $L_{Arm} = \text{Distanz(Shoulder, Elbow)} + \text{Distanz(Elbow, Wrist)}$
4. **Schulterbreite**
   - Relevant für die Lenkerbreite.
   - **Realisierung:** Direkter Abstand zwischen `LShoulder` und `RShoulder` in einer frontalen Aufnahme.
5. **Oberschenkel- und Unterschenkellänge**
   - Relevant für den Kniewinkel und das Nachsitzen des Sattels.
   - **Realisierung:** Distanz(`Hip`, `Knee`) bzw. Distanz(`Knee`, `Ankle`).

## 4. Machbarkeitsbewertung und Herausforderungen

**Ist das Konzept machbar?**
**Ja, prinzipiell ist das Vorhaben absolut machbar.** Da Sports2D hochpräzise Gelenkkoordinaten liefert und die Körpergröße als Referenzmaßstab dient, lässt sich eine Bike-Fitting-Analyse daraus programmieren.

Allerdings gibt es **Herausforderungen und Limitierungen**, die für einen praxistauglichen Einsatz berücksichtigt werden müssen:

1. **Perspektivische Verzerrung (2D-Problematik)**
   - Sports2D arbeitet in 2D. Wenn Arme oder Beine auf die Kamera zu oder von ihr weg angewinkelt sind, erscheinen sie im 2D-Bild kürzer (Verkürzungseffekt / Foreshortening).
   - *Lösungsansatz:* Die Segmentlängen dürfen nur in solchen Frames gemessen werden, in denen sich das jeweilige Körperteil exakt parallel zur Kamera befindet (z.B. Arme hängen seitlich flach herunter in der Frontalansicht).
2. **Bestimmung der wahren Kopfhöhe**
   - Pose-Modelle erkennen zwar den Kopf/Nase/Hals, wissen aber nicht immer präzise, wo exakt die Haargrenze/der oberste Punkt des Scheitels ist. Das kann den Skalierungsfaktor um 1-3 % verfälschen.
3. **Anordnung der Kamera**
   - Die Kamera sollte auf halber Höhe des Körpers positioniert werden, um Linsenverzerrungen zu minimieren. Steht das Handy auf dem Boden und ist nach oben gekippt, werden die Beine im Bild überproportional lang dargestellt.
4. **Benötigte Ansichten**
   - Für die Messung von Rumpf, Armen und Beinen eignet sich eine **Seitenansicht (Profil)** am besten.
   - Für die Schulterbreite ist zwingend eine **Frontalansicht** nötig.
   - *Lösung:* Der Nutzer muss ein kurzes Video aufnehmen, bei dem er sich langsam um 90 Grad dreht (oder in beiden Posen verharrt), sodass das Programm automatisch die besten Frames für die verschiedenen Längen heraussucht.

## 5. Fazit und nächste Schritte

Die Nutzung von Sports2D zur Berechnung von Bike-Fitting-Maßen anhand der Gesamtkörpergröße ist logisch fundiert und **technisch sehr gut umsetzbar**.

Für eine prototypische Umsetzung wäre der nächste Schritt, ein Python-Skript zu schreiben, welches:
1. Ein Video einliest und mit Sports2D die `HALPE_26`-Keypoints extrahiert.
2. Einen Algorithmus anwendet, der die längsten Ausdehnungen der Gliedmaßen im gesamten Video sucht (um perspektivische Verkürzungen zu filtern).
3. Die Segmentlängen berechnet, mit dem Umrechnungsfaktor multipliziert und als Bericht für das Bike-Fitting (z.B. als PDF oder in der Konsole) ausgibt.