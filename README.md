> [!NOTE]
> **🚧 Proiect Personal & Work in Progress**  
> Această integrare este un proiect personal, dezvoltat din pasiune. Este într-o continuă evoluție, iar noi optimizări și funcționalități vor fi adăugate pe măsură ce îmi vin idei noi. 
> Folosiți-l cu încredere și nu ezitați să propuneți îmbunătățiri! ✨

![logo-main](https://github.com/user-attachments/assets/5841ec01-81c9-4c25-8373-b09d9ba11fe6)

# E-ON România - Integrare pentru Home Assistant 🏠🇷🇴

Această integrare pentru Home Assistant oferă **monitorizare completă** a datelor E-ON România. Acum suportă **conturi multiple** și **toate contractele** asociate unui singur cont de utilizator! 🚀

## 🌟 Noutăți (v2.0)

- **🔐 Autentificare Simplificată**: Te loghezi doar cu email și parolă. Fără coduri de încasare manuale!
- **multi-Contract**: Un singur cont -> Toate locurile de consum. Integrarea detectează automat toate contractele tale.
- **🔢 Input Index Integrat**: Nu mai ai nevoie de helperi. Fiecare contract are propriul câmp pentru introducerea indexului.

---

## 🌟 Caracteristici Principale

### ⚡ Monitorizare Contracte & Consum
Fiecare contract este reprezentat ca un **Device** separat în Home Assistant, grupând toți senzorii relevanți:

- **Senzor `Date contract`**: Informații detaliate (preț kWh, adresă, distribuitor, date expirare revizii).
- **Senzor `Index curent`**: Ultimul index citit, perioada de citire activă.
- **Senzor `Sold & Facturi`**:
    - **Factură restantă**: Alertă dacă există facturi neplătite.
    - **Notificări Plată**: Sume scadente.
    - **Sold Prosumator**: Pentru cei care injectează în rețea.
    - **Portofel Utilizator**: Soldul contului MyLine.

### 📅 Istoric & Arhive
- **Arhivă consum**: Istoric lunar consum (mc/kWh).
- **Arhivă index**: Istoric indexuri declarate.
- **Arhivă plăți**: Istoricul plăților efectuate.
- **Convenție consum**: Detalii despre convenția de consum stabilită.

### 📤 Transmitere Index (Nou!)
- **Entitate `Index de transmis` (`number`)**: Câmp dedicat pentru fiecare contract unde introduci indexul.
- **Buton `Trimite index` (`button`)**: Trimite valoarea introdusă direct către E-ON.
- **Senzor `Citire permisă`**: Îți spune când poți transmite indexul.

---

## ⚙️ Configurare

### 🛠️ Configurare prin UI (Recomandat)
1. Mergi la **Settings > Devices & Services > Add Integration**.
2. Caută **E-ON România**.
3. Introdu:
   - **Nume utilizator**: Adresa de email a contului E-ON MyLine.
   - **Parolă**: Parola contului.
4. **Gata!** Integrarea va descoperi automat toate contractele tale și va crea dispozitive pentru ele.

~~*Notă: Nu mai este necesar Codul de Încasare la configurare!*~~

---

## 🚀 Instalare

### 💡 Prin HACS (Recomandat):

[![Deschide instanța ta Home Assistant și depozitul în Magazinul Comunității Home Assistant.](https://my.home-assistant.io/badges/hacs_repository.svg)](https://my.home-assistant.io/redirect/hacs_repository/?owner=https%3A%2F%2Fgithub.com%2Ftbutiu&repository=lejer_eonromania&category=Bills)

1. Apasă pe butonul de mai sus pentru a deschide depozitul direct în HACS.
2. Sau adaugă manual [depozitul](https://github.com/tbutiu/lejer_eonromania) în HACS > Integrations > Custom repositories.
3. Caută **E-ON România** și instalează.
4. Restart Home Assistant.

### ✋ Manual:
1. Descarcă [ultima versiune](https://github.com/tbutiu/lejer_eonromania/releases).
2. Copiază folderul `custom_components/lejer_eonromania` în folderul `config/custom_components` al serverului tău.
3. Restart Home Assistant.

---

## ✨ Exemple de Utilizare

### 📤 Automatizare Index
Trimite o notificare pe telefon când se deschide perioada de citire pentru un contract.

```yaml
alias: "Notificare Citire E-ON"
trigger:
  - platform: state
    entity_id: sensor.lejer_eonromania_citire_permisa_00XXXXXXXXXX
    to: "Da"
action:
  - service: notify.mobile_app_phone
    data:
      title: "E-ON: Se poate transmite indexul! 📝"
      message: "Perioada de citire este deschisă pentru locul de consum X."
```

### 🔢 Card Transmitere Index
Adaugă un card simplu în dashboard pentru a trimite indexul rapid.

```yaml
type: entities
title: Transmitere Index Gaz
entities:
  - entity: sensor.lejer_eonromania_citire_permisa_00XXXXXXXXXX
    name: Status
  - entity: number.lejer_eonromania_index_input_00XXXXXXXXXX
    name: Introdu Index
  - entity: button.lejer_eonromania_trimite_index_00XXXXXXXXXX
    name: Trimite Acum
```

---

## ❓ Întrebări Frecvente (FAQ)

- **Am mai multe contracte, trebuie să configurez de mai multe ori?**  
  Nu. O singură configurare cu contul tău de email va aduce toate contractele automat.

- **Unde găsesc indexul de transmis?**  
  Caută entitatea `number.lejer_eonromania_index_input_...` asociată dispozitivului contractului tău.

Vezi [FAQ.md](./FAQ.md) pentru mai multe detalii.

---

## ☕ Susține Proiectul

Dacă această integrare îți face viața mai ușoară, poți susține dezvoltarea!

[![Buy Me A Coffee](https://img.shields.io/badge/Buy%20Me%20A%20Coffee-Donează-orange?style=for-the-badge&logo=buy-me-a-coffee)](https://buymeacoffee.com/lejer)

Mulțumesc! 🤗

---

## 🧑‍💻 Contribuții & Credite

Proiect Open Source. Contribuțiile sunt binevenite prin Pull Requests.
Bazat pe munca inițială a lui [@cnecrea](https://github.com/cnecrea). Dezvoltat și menținut de [@tbutiu](https://github.com/tbutiu).
