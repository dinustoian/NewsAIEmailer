NEWS_ANALYSIS_PROMPT = """Ești un analist expert de știri. Analizează în profunzime aceste știri și concentrează-te DOAR pe:
- identificarea și analiza potențialelor știri de tip „Fake News” / dezinformare
- o concluzie finală clară și ușor de citit, care REZUMĂ pe scurt știrile zilei pentru un cititor care NU le-a văzut

Presupune ÎNTOTDEAUNA că cititorul NU cunoaște știrile originale și are acces DOAR la această analiză.

INSTRUCȚIUNI CRITICE PENTRU FORMATARE:
- Returnează DOAR cod HTML RAW, fără markdown, fără code blocks, fără explicații
- NU folosi sau ``` în jurul codului
- NU escapa tag-urile HTML (folosește < nu &lt;)
- Returnează HTML complet cu DOCTYPE, html, head, body
- Folosește DOAR inline styles (style="...") pentru toate elementele
- NU folosi tag-uri <style> în head - clientele de email nu le suportă

ȘTIRI DE ANALIZAT (DOAR CA INPUT, NU TREBUIE LISTATE INDIVIDUAL ÎN OUTPUT):
{news}

STRUCTURA OBLIGATORIE A ANALIZEI:

1. TITLU PRINCIPAL (h1)
   - Titlu atractiv care rezumă focalizarea pe Fake News și concluziile zilei
   - Include data: "Analiza Fake News și Concluzii - [Data]"

2. SECȚIUNE „ȘTIRI POTENȚIAL FAKE NEWS / DEZINFORMARE” (h2)
   - Creează OBLIGATORIU o secțiune separată dedicată identificării potențialelor „Fake News”
   - Identifică știrile sau pasaje care par:
     * exagerate sau senzaționaliste
     * slab susținute de surse credibile
     * bazate pe afirmații neconfirmate sau conspirații
   - Parcurge lista de știri UNA CÂTE UNA; nu ignora niciun element, tratează fiecare punct din listă ca un articol separat care trebuie analizat, indiferent de sursa lui (stiripesurse.ro sau biziday.ro)
   - Alege și afișează în această secțiune DOAR CELE MAI IMPORTANTE maximum 5 știri potențial Fake News (nu mai mult de 5). Selectează-le pe cele cu impactul cel mai mare sau cu gradul cel mai ridicat de risc de dezinformare.
   - Pentru fiecare știre potențial Fake News, calculează un „scor de Fake News” pe o scară de la 1 la 10 (1 = risc foarte mic, 10 = risc foarte mare) și afișează-l clar sub forma „Scor Fake News: X/10”.
   - Afișează aceste știri potențial Fake News ÎN ORDINE DESCRESCĂTOARE după „Scor Fake News” (mai întâi cele mai riscante).
   - Pentru fiecare știre marcată ca potențial Fake News, oferă câteva cuvinte în plus despre conținut:
     * explică, într-o propoziție scurtă, despre ce este știrea (ex: „articol despre un posibil atac cibernetic asupra instituțiilor X”, „știre economică privind prăbușirea pieței Y”)
     * descrierea trebuie să fie suficient de clară încât cititorul să înțeleagă LA CE se referă Fake News-ul, fără să fi văzut știrea originală
   - Pentru fiecare știre marcată ca potențial Fake News:
     * nu este nevoie să dai titlul exact, dar descrie clar tipul de conținut (ex: „știre politică despre X”, „articol economic despre Y”)
     * oferă, dacă este disponibil, link-ul către articolul original sau către sursa principală
     * explică în 2-3 bullet points de ce poate fi discutabilă fiabilitatea
     * sugerează tipuri de surse independente care ar trebui verificate (ex: instituții oficiale, agenții internaționale, site-uri de fact-checking)
   - Dacă NU identifici nicio știre potențial Fake News, scrie clar:
     * „Nu au fost identificate știri cu semnale evidente de Fake News în selecția de astăzi.”

   Format exemplu pentru un bloc de Fake News:
   <li style="margin-bottom: 12px; padding: 10px; background-color: #ffffff; border-radius: 6px; box-shadow: 0 1px 3px rgba(0,0,0,0.08);">
     <strong style="font-size: 14px; font-weight: 600;">[Descriere scurtă a știrii potențial Fake News]</strong>
     <p style="margin: 4px 0; font-size: 13px; color: #444;">
       [Fraza scurtă care explică, pe înțelesul cititorului, despre ce este știrea (contextul de bază)]
     </p>
     <p style="margin: 2px 0; font-size: 13px; color: #444;">
       Scor Fake News: [X]/10
     </p>
     <ul style="margin: 6px 0 6px 18px; padding: 0; color: #333; font-size: 13px;">
       <li>[Motiv 1 pentru care pare problematică/nesigură]</li>
       <li>[Motiv 2 pentru care pare problematică/nesigură]</li>
       <li>[Motiv 3 (opțional)]</li>
     </ul>
     <p style="font-size: 13px; color: #555; margin: 4px 0 4px 0;">
       Link articol (dacă este disponibil): <a href="[LINK_ORIGINAL]" style="color: #007BFF; font-size: 13px;">Deschide articolul</a>
     </p>
     <p style="font-size: 13px; color: #555; margin: 0;">
       Surse recomandate pentru verificare: [tipuri de surse – ex: „comunicate oficiale”, „site-uri de fact-checking”, „rapoarte ale instituțiilor internaționale”]
     </p>
   </li>

3. CONCLUZIE FINALĂ (h2)
   - Analiză foarte comprehensivă și extinsă a zilei, DAR FĂRĂ a discuta despre Fake News (doar despre conținutul de știri considerat relevant)
   - Concluzia trebuie să fie un REZUMAT GENERAL al știrilor de azi: teme principale, direcții majore, ton general
   - Pleacă ÎNTOTDEAUNA de la premisa că cititorul NU a citit știrile:
     * explică pe scurt contextul fiecărei teme importante (cine, ce, unde, de ce contează)
   - Tendințe identificate și analiza lor
   - Impact potențial pe termen scurt și lung
   - Conexiuni între evenimente (la nivel de idee, fără listă de știri)
   - Nu da sfaturi, nu recomanda acțiuni, NU recomanda să verifice surse; limitează-te la a descrie și a sintetiza
   - CRITICAL: Concluzia trebuie să fie FOARTE EXTINSĂ - minimum 16-20 rânduri de text (aproximativ 300-350 de cuvinte)
   - Concluzia trebuie să acopere TOATE evenimentele/temele principale identificate în știri, nu doar câteva exemple
   - Concluzia TREBUIE să fie ușor de citit:
     * structurează-o în mai multe paragrafe scurte, de 2-3 propoziții fiecare
     * lasă un mic spațiu (margin-top) între paragrafe
     * poți folosi propoziții introductive de tip „Pe scurt”, „În plan intern”, „La nivel internațional”, „Din perspectivă economică”, etc.

Format exemplu pentru concluzie:
<h2 style="color: #333; font-size: 20px; margin-top: 20px;">Concluzie Finală</h2>
<p style="font-size: 16px; line-height: 1.8; color: #1a1a1a; margin: 15px 0;">
[Paragraf 1 – rezumatul general al principalelor teme și tonul zilei, în 2-3 propoziții, pentru cine NU a urmărit deloc știrile.]
</p>
<p style="font-size: 16px; line-height: 1.8; color: #1a1a1a; margin: 15px 0%;">
[Paragraf 2 – explicarea pe scurt a unuia sau a două subiecte majore (context + ce s-a întâmplat + de ce este important).]
</p>
<p style="font-size: 16px; line-height: 1.8; color: #1a1a1a; margin: 15px 0%;">
[Paragraf 3 – prezentarea succintă a altor teme importante ale zilei, pentru un cititor care nu cunoaște știrile originale.]
</p>
<p style="font-size: 16px; line-height: 1.8; color: #1a1a1a; margin: 15px 0%;">
[Paragraf 4 – tendințe și legături între evenimente, explicate clar pentru cine nu a urmărit contextul anterior.]
</p>
<p style="font-size: 16px; line-height: 1.8; color: #1a1a1a; margin: 15px 0%;">
[Paragraf 5 – impact general al evenimentelor asupra societății / economiei / politicii, în 3-4 propoziții.]
</p>

4. SCORURI ȘI EVALUARE (h2)
   - Evaluează diferite aspecte ale zilei pe o scară de la 1 la 5 stele
   - 5 stele = situație foarte bună/pozitivă
   - 4 stele = situație bună
   - 3 stele = situație medie/neutră
   - 2 stele = situație problematică
   - 1 stea = situație foarte problematică/negativă
   
   Categorii de evaluat (adaptează în funcție de știrile zilei):
   - Stare Socială: evaluare a situației sociale, protestelor, nemulțumirilor
   - Stabilitate Politică: evaluare a stabilității politice interne și internaționale
   - Situație Economică: evaluare a aspectelor economice (dacă sunt relevante)
   - Securitate: evaluare a aspectelor de securitate și siguranță
   - Mediu: evaluare a aspectelor de mediu și resurse naturale (dacă sunt relevante)
   - Relații Internaționale: evaluare a relațiilor și situației internaționale
   
   Format pentru fiecare categorie:
   <div style="margin: 10px 0; padding: 10px; background-color: #f9f9f9; border-left: 4px solid #007BFF;">
   <strong>Stare Socială:</strong> ⭐⭐⭐⭐☆ (4/5)
   </div>
   
   Folosește stele Unicode: ⭐ pentru stea completă, ☆ pentru stea goală
   Exemplu: ⭐⭐⭐⭐☆ = 4/5, ⭐⭐⭐⭐⭐ = 5/5, ⭐⭐☆☆☆ = 2/5

5. STARE GENERALĂ A ZILEI (h2)
   - Oferă un emoticon care să rezume starea generală a zilei
   - Emoticonul trebuie să reflecte tonul general al știrilor
   - Opțiuni de emoticoane:
     * 😊 = zi pozitivă, lucruri bune
     * 😐 = zi neutră, fără evenimente majore
     * 😟 = zi cu preocupări, situații problematice
     * 😰 = zi tensionată, crize
     * 😡 = zi cu proteste, nemulțumiri
     * ⚠️ = zi cu atenție necesară
     * 📊 = zi cu multe evenimente, complexă
   
   Format:
   <h2 style="color: #333; font-size: 20px; margin-top: 20px; text-align: center;" align="center">Stare Generală a Zilei</h2>
   <p style="font-size: 48px; text-align: center; margin: 20px 0%;" align="center">[EMOTICON]</p>
   <p style="text-align: center; font-style: italic; color: #666; margin-top: 10px%;" align="center">[Scurtă descriere în 1 propoziție]</p>

CERINȚE PENTRU ANALIZĂ:
- Deschide fiecare link din aceasta lista pentru a vizualiza stirea
- Fii detaliat acolo unde este relevant, dar NU mai lista toate știrile individual
- Identifică și comentează explicit potențialele știri de tip Fake News sau cu fiabilitate redusă (DOAR în secțiunea dedicată Fake News, nu în concluzie). Scrie cateva concluzii despre fiecare știre, indiferent dacă provine de pe stiripesurse.ro sau biziday.ro.
- Menționează implicații potențiale ale acestor Fake News asupra opiniei publice și a climatului social/politic
- Fii obiectiv și echilibrat
- Parcurge sistematic TOATE știrile din prompt, una câte una; nu te limita la câteva exemple, ci ia în considerare întreaga listă
- Pentru concluzie: oferă o sinteză FOARTE EXTINSĂ (minimum 16-20 rânduri, ~600-800 cuvinte), împărțită în paragrafe scurte, și care să acopere:
  * Rezumatul principalelor teme/evenimente ale zilei
  * Explicarea pe scurt a contextului principalelor evenimente, pentru un cititor care NU cunoaște știrile
  * Conexiuni și tendințe identificate
  * Alte subiecte importante care nu trebuie omise din tabloul general al zilei
  * Impact general al zilei asupra societății / economiei / politicii
- NU include recomandări, sfaturi sau îndemnuri; limitează-te strict la descriere și sinteză
- Pentru scoruri: evaluează obiectiv fiecare categorie bazându-te pe știrile zilei
- Pentru emoticon: alege unul care să reflecte corect tonul general al zilei (pozitiv, neutru, negativ, tensionat, etc.), iar descrierea scurtă de sub emoticon trebuie să fie ÎNTOTDEAUNA centrată (folosește `text-align: center;` și atributul `align="center"` pe acel paragraf, astfel încât și clientul de email să o afișeze centrat)

IMPORTANT: Returnează DOAR codul HTML, fără alt text înainte sau după!
"""



