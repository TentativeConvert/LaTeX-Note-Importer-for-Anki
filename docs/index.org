#+SETUPFILE: theme/theme.setup

#+AUTHOR: Marcus Zibrowius
#+TITLE: LaTeX Note Importer for Anki

    /LaTeX Note Importer is an add-on for Anki, an open-source flash-card program developed and maintained by Damien Elmes. As the name says, the add-on provides functionality for importing notes from LaTeX files. This allows you to create Anki notes in your favourite editor or IDE. Of course, this is mainly useful for notes that contain a lot of LaTeX to begin with, for example mathematical notes./

* Installation<<install>>
  You will need the following prerequisites:

  + LaTeX:  you need a local (La)TeX installation.
  + Anki:  you need a [[http://ankisrs.net/#download][local installation of Anki]], and it needs to be 
    [[http://ankisrs.net/docs/manual.html#latex-support][set up to interact with your local TeX installation]].
  Assuming you have these, installing LaTeX Note Importer is easy.
  In Anki’s main window, choose =Tools= =>= =Add-ons= =>= =Browse & Install...=, enter
  #+BEGIN_QUOTE
  #+BEGIN_CENTER
  1199027445
  #+END_CENTER
  #+END_QUOTE
  and click =[OK]=. Then restart Anki.

* Examples
** Minimal example
   Let's have a look at a fairly minimal example file that LaTeX Note Importer can deal with:
   #+BEGIN_SRC LaTeX
    \begin{document}
    \begin{note}
       \begin{field}
           Is it true that \(1 + 1 = 0\)?
       \end{field}
       \begin{field}
           Yes and no. The equation
           \begin{equation*}
                1+1 = 0
           \end{equation*}
           holds only in characteristic two.
       \end{field}
    \end{note}
    \end{document}
   #+END_SRC
   Importing this file into Anki will create a new note with two fields. The contents of each field will be enclosed in Anki's =[latex] ...[/latex]= commands. (If you do not think this is a good idea, see the [[latex-in-template][FAQ below]].) For example, in Anki's built-in editor, the first field of the imported note will be displayed as follows:

   #+BEGIN_SRC LaTeX
    [latex]
    Is it true that \(1 + 1 = 0\)?
    [/latex] 
    #+END_SRC
   In order for the importer to work correctly, the tex-file needs to be saved in utf-8 encoding. This is the same prerequisite as required by Anki's built-in text importer. If you use emacs for text editing, you can force the file to be saved in utf-8 by adding =% -*- coding:utf-8 -*-= to the beginning of your file.
  
** Compilable example
   Of course, we would also like our LaTeX file to be compilable! We should therefore add a line that informs the LaTeX compiler about the encoding we are using, and we should define the =note= and =field= environments. Here's a compilable version of the above example:

    #+BEGIN_SRC LaTeX
    % -*- coding:utf-8 -*-
    \documentclass[12pt]{article}
    \usepackage[utf8]{inputenc}
    \newenvironment{note}{\paragraph{NOTE:}}{}
    \newenvironment{field}{\paragraph{field:}}{}
    \begin{document}
    \begin{note}
       \begin{field}
           Is it true that \(1 + 1 = 0\)?
       \end{field}
       \begin{field}
           Yes and no. The equation
           \begin{equation*}
                      1+1 = 0
           \end{equation*}
           holds only in characteristic two.
       \end{field}
    \end{note}
    \end{document}
    #+END_SRC
    There is no restriction on the number of notes you can include in a single LaTeX file, nor on the number of fields you can include in a note. Unlike Anki's built-in text importer, LaTeX Note Importer does not require each note to have the same number of fields. However, you should keep in mind that you will have to specify a single Anki note type when importing the file; notes should not have more fields than this note type provides. And, if you use tags, it’s best to have at least one note in your file that has exactly as many fields as the note type provides: see [[import-tags][details on tag import]].
    
    On first reading, you’ll probably now want to skip down to the [[import][instructions for importing]].

** More examples
   The following files are provided mainly for inspiration.
   
*** A basic example
    #+BEGIN_CENTER
    [[file:demo.tex]]\\
    [[file:demo.pdf]]
    #+END_CENTER

    You can import =demo.tex= into Anki as it is.  Note however that in order for the notes to compile in Anki, you still need to [[import-preamble][manually copy the LaTeX preamble into Anki]].

*** An example in which the pdf-output can be cut into paper cards
    #+BEGIN_CENTER    
    [[file:TopoCards.tex]]\\
    [[file:TopoCards.pdf]]\\
    [[file:TopoCards.apkg]]
    #+END_CENTER

    Again, you can import =TopoCards.tex= into Anki as it is, but you will need to [[import-preamble][import the preamble manually]]. Alternatively, you can first import the example deck (*.apkg) into Anki: this will in particular create a note type compatible with the LaTeX file, i.e. with the correct number of fields, and with the correct LaTeX preamble.


* Syntax<<syntax>>
** Fields
   Altogether, LaTeX Note Importer supports four different field types:

   + LaTeX fields: =\begin{field} …some LaTeX… \end{field}=\\
     The contents of these fields are surrounded by =[latex]…[/latex]= when imported. Moreover, the following special characters are replaced by their html-equivalents: =<=, =>=, =&=. (This is necessary. Anki will translate them back when sending them to the LaTeX compiler.)

   + Short LaTeX fields: =\xfield{ …some LaTeX… }=\\
     These fields work like the previous ones, except that no additional line breaks are inserted after =[latex]= and before =[/latex]=. The idea is to use this field type primarily for short, single-line LaTeX code, which will then remain single-line upon importing. For example, you could use this type of field for prompts/questions, and the usual field environment for answers.
   
   + Plain text fields: =\begin{plain} …some text… \end{plain}=\\
     As the name indicates, these fields can be used to import plain text -- the text will not be included in =[latex]…[/latex]=, nor will any other operations be performed on it.
    
   + Short plain text fields: =\xplain{ …some text… }=\\
     Like the previous one. For example, this field can be used for note IDs (see the section on [[update][updating notes]]). 

   Of course, you will need to define each field type that you use in the preamble of your file in order for the file to be compilable.

** Tags
   You can add tags to the notes in your LaTeX file using the command:
   #+BEGIN_SRC LaTeX
    \tags{ tag1 tag2 … } 
   #+END_SRC
   
   Again, you will also need to add some definition of this command to the preamble in order for the file to be compilable, for example:
   #+BEGIN_SRC LaTeX
    \newcommand*{\tags}[1]{\paragraph{tags: }#1} 
   #+END_SRC
   
   The scope of the tags =tag1=, =tag2= … depends on the relative position of the =\tags=-command:

   + *global tags:* If the command is placed in between notes, the tags =tag1=, =tag2=, … will be applied to all the following notes, until another =\tags=-command in between notes is encountered. These tags do not accumulate, i.e. a global tag command always overwrites all preceding global tag commands.
    
   + *local tags:* If the command is placed inside a note (but not inside a field), =tag1=, =tag2=, … will be applied to the current note only. These tags are applied in addition to the global tags, and they accumulate within a note. 

   The behaviour is best illustrated with an example:
   #+BEGIN_SRC LaTeX
    \tags{g1 g2}
    \begin{note}
       \tags{l1}
       \begin{field}
           Is it true that \(1 + 1 = 0\)?
       \end{field}
       % This note has tags g1, g2, l1.
    \end{note}

    \begin{note}
       \begin{field}
           Is it true that \(1 + 1 = 1\)?
       \end{field}
       % This note has tags g1, g2.
    \end{note}

    \tags{g3}
    \begin{note}
       \tags{l2}
       \begin{field}
           Is it true that \(1 + 1 = 2\)?
       \end{field}
       \tags{l3}
       % This note has tags g3, l2, l3.
    \end{note}
   #+END_SRC

** Comments
   All text in between notes or in between fields is ignored by the importer. In particular, you can use this space for adding comments in your file. LaTeX comments within fields are also handled correctly as long as they are used within sane limits. Fragments of the form
   #+BEGIN_SRC LaTeX
    \begin% some comment
    {field}
   #+END_SRC
   will definitely confuse the importer, even though they do not seem to confuse LaTeX compilers.


* Porting<<porting>>
** Import<<import>>
   You can import your LaTeX file using either the menu (=File= =>= =Import...=) or the =[Import File]= button at the bottom of the main Anki window. A dialog window allows you to specify which deck to import the notes to, which note type to base them on, and how to map the imported fields onto the fields of that note type. (By default, the fields are kept in the order in which they appear in the LaTeX file.) Moreover, you can choose between the following three options:
   #+BEGIN_QUOTE
   =Update existing notes when first field matches= \\
   =Ignore lines where first field matches existing note= \\
   =Import even if existing note has same first field=
   #+END_QUOTE

   This import dialog is part of core Anki, so the wording is perhaps not perfectly adapted to LaTeX files—read "ignore notes" for "ignore lines".

*** Preamble<<import-preamble>>
    The preamble of the LaTeX file is not imported. You can configure the LaTeX preamble used by Anki by selecting (=Tools= =>= =Manage Note Types...=) in the main menu, choosing the relevant note type and clicking on the =[Options]= button.

*** Tags<<import-tags>>
    In the current version of LaTeX Note Importer, tags are only imported correctly if the (maximum) number of fields per note in the LaTeX file matches the number of fields of the note type selected in the import dialog.

    For example, suppose our note type has just the two fields =Front= and =Back=, and accordingly each note in our LaTeX file also has two fields. If any of these notes has a tag, then the import dialog will show up with three fields. It will look something like this:
    #+BEGIN_QUOTE
    Field 1 of file is: mapped to =Front=\\
    Field 2 of file is: mapped to =Back=\\
    Field 3 of file is: mapped to =Tags=
    #+END_QUOTE

    This is what we want! The mysterious =Field 3= contains the tags that we specified with the =\tags=-command in our LaTeX file, and if we do not change the default association of =Field 3= with =Tags=, then these tags will be imported correctly.

    I won't attempt to defend the shortcomings of this user interface, but I'll include the following ascii art purely for its aesthetic value:

    :              +------------+                        +--------+
    :    LaTeX   --+ LaTeX Note +--->      list of    ---+ IMPORT +-->     Anki
    :    file    --+  Importer  +--->   field values  ---+ DIALOG +-->   database
    :              +------------+                        +--------+

    Back to our example. What happens if our note type has more fields than occur in the notes in our LaTeX file? Suppose, for instance, that our note type has a third field =Hints=, but we are using the same LaTeX file as before. Then the import dialog will instead display as:
    #+BEGIN_QUOTE
    Field 1 of file is: mapped to =Front=\\
    Field 2 of file is: mapped to =Back=\\
    Field 3 of file is: mapped to =Hints=
    #+END_QUOTE
    The tags we specified in the LaTeX file are again displayed as a mysterious =Field 3=, but now they will be imported as =Hints= instead of tags! We can easily correct this insane default behaviour, however, by clicking on the =Change= button next to =Hints= in the dialog and selecting =Tags= instead.

    Finally, if at least one of the notes in our LaTeX file does contain a third field, everything is automatically fine again. The dialog comes up with an additional =Field 4=, and this field is correctly mapped to =Tags=:
    #+BEGIN_QUOTE
    Field 1 of file is: mapped to =Front=\\
    Field 2 of file is: mapped to =Back=\\
    Field 3 of file is: mapped to =Hints=\\
    Field 4 of file is: mapped to =Tags=
    #+END_QUOTE

*** Updating notes<<update>>
    Suppose you have imported some notes and started learning with them.  Suppose that, after a while, you notice some mistakes or inconsistencies that you would like to correct.  Is it possible to make these corrections in your original LaTeX file and reimport it without losing all of Anki’s scheduling information for this deck? 

    The answer is YES, you can.  As long as you don’t edit the first field of each note, you can update them in Anki by editing them in your LaTeX file and choosing the option
    #+BEGIN_QUOTE
=Update existing notes when first field matches=
    #+END_QUOTE
    when you import.

    So, what if you also want to edit the first field?  The trick is to plan ahead and reserve the first field of each note for a unique ID that will never change. The =\xplain-fields= are provided with exactly this purpose in mind.  For more details, see the [[course][step-by-step guide on how to maintain a deck for a lecture course]].

** Export<<export>>
   To export a deck into a tex file, go to =File= =>= =Export...= in the main menu and select =[Notes in LaTeX (*.tex)]= as export format. 


* Maintaining a deck for a lecture course<<course>>
  The following is a step-by-step guide explaining how to create and maintain an Anki deck for a maths lecture course as you go along.  The idea is to create and import cards each week as the course progresses, but in such a way that you can still go back and make changes later on. 
  
** Preparations 
   1. If you haven’t already done so, follow the [[install][installation instructions]] above.
   2. Download the example file  [[file:TopoCards.tex]]. You will create and maintain all notes in this single file.  

   3. Adapt the LaTeX preamble of the file to your needs.  Try as much as possible to include all packages and macros that you will need for this particular course.  Every time you change the preamble later, you will also have to repeat Step 5 below.

   4. Download the example deck [[file:TopoCards.apkg]] and import it into Anki (=File= =>= =Import...=).  This will create a deck called =Maths::TopoCards= and a note type called =TopoNote=.  You can rename and edit the note type under =Tools= =>= =Manage Note Types…=.  Be sure to keep the first field for the ID.

   5. If you changed the LaTeX preamble in Step 2, then copy the preamble of your LaTeX file to Anki:  =Tools= =>= =Manage Note Types= =>= =[TopoNote]= =>= =Options…= . 
  
     (In the case of our example file =TopoCards.tex=, only a part of the preamble is included in the settings of =TopoNote=. This is because =TopoCards.tex= uses some raw tex commands to produce its pdf output, and these commands throw errors in Anki.)


** Weekly workflow
    [[syntax][For the general syntax to use in the LaTeX file, see above]].  Here, we just explain the weekly workflow.

    1. After the last note in the file, insert 
       #+BEGIN_SRC LaTeX
\tags{LectureN} 
      #+END_SRC
      or a similar line, where =N= is the number of the current lecture.  This will tag each of the following cards with the tag “LectureN”.  Don’t put a whitespace between =Lecture= and =N=, as this will create two separate tags!  
      ([[http://ankisrs.net/docs/manual.html#using-decks-appropriately][Using tags for sorting cards into lectures is better than using (sub)decks.]])

    2. Write the notes for this week/lecture below that line.
       Each note should begin with a field containing a unique ID.  For example, you can just number your notes consecutively as you type them, or use a UUID generator.  This will allow notes to be updated on successive imports.
       The Anki note template provided with the example deck accepts at most 8 further fields (4 prompts and 4 answers).  Don’t put more fields into a single note.

       If you haven’t messed up, it should be possible to process the file with =pdflatex=.  So you can check your notes before importing them into Anki. 

    3. Import the LaTeX file into Anki (=File= =>= =Import…=).
       In the import dialog, choose
       #+BEGIN_QUOTE
=Update existing notes if first line matches.=
       #+END_QUOTE
       and, if you used tags in the file as recommended, make sure the last field is mapped to =Tags=.

** Sharing/publishing
     Export your deck as an  =*.apgk-file= via =Gear icon next to deck= =>= =Export=.
     In the export dialog, choose the following settings:
     
     #+BEGIN_QUOTE
        =Export format: Anki Deck Package=\\
        +=Include scheduling information=+\\
        =Include media=
     #+END_QUOTE


 You can share the =*.apkg-file= file with friends or publish it on the web. 


 
  

* FAQ 
  You can contact me using any of the means listed on my [[http://reh.math.uni-duesseldorf.de/~zibrowius/][homepage]].  Here, I just answer some of the most likely questions.

** <<latex-in-template>>Why not keep the [latex]-commands in a card template?

  Why does the importer encapsulate all fields with [latex] … [/latex]? Wouldn't it be more sensible to import fields as they are and instead insert the [latex]-commands into our card template?

  Although this does work sometimes, [[http://ankisrs.net/docs/manual.html#media-&-latex-references][the Anki manual explicitly discourages this approach]]:
  #+BEGIN_QUOTE
  Media references to fields are not allowed. They may or may not display during review, and will not work when checking for unused media, importing/exporting, and so on. Examples that won't work:
  
  :    […] 
  :
  :    [latex]{{Field 1}}[/latex] 
  
  Instead, you should include the media references in the field. 
  #+END_QUOTE
  
** Why has the mechanism for importing tags changed?
    With previous versions of LaTeX Note Importer, it was impossible to update the tags of existing notes. 
    This is due to a limitation of the core Anki importer: it does not update tags of existing notes unless these tags are imported as an additional field.

** Where can I find the code?
    Once the add-on is installed, you can find the code in the folder =…/​Anki/​addons/​latexbiport=.



    
* COMMENT experiments
  - Muss der relevante "Note type" bereits existieren, und kann er mit importiert werden ? 
    → Kann  mit importiert werden.
  - Wie sieht es mit der Preamble aus?
    
* COMMENT instructions for "my" students:
** Option Zuschauer
  - Anki installieren.
  - Wöchentlich neues Deck herunterladen.
  - Täglich Karten lernen.

  Bei dieser Option kann man die Karten nicht selbst bearbeiten.  Wer aus Versehen eine Karte bearbeitet hat und im Nachhinein merkt, dass sie nicht mehr richtig angezeigt wird, muss das Deck neu importieren.  

  Fehler auf den Karten sind  gegebenfalls an XXX zu melden. 
    
** Option Freiwilliger
   Wer bei der Erstellung der Karten helfen oder mitmachen möchte, meldet sich am besten bei mir. 

** Option Eigenbrödler
   Um die Karten selbst bearbeiten zu können,  muss TeX lokal instaliert und richtig eingestellt sein.  Siehe hierzu das Anki-Handbuch.  Wenn man nicht aufpasst, werden alle eigenen Änderungen an den Karten allerdings bei der wöchentlichen Aktualisierung des Decks überschrieben. 
   
   Mehr Informationen bei mir / on my Anki page.  Dort ist auch detailliert beschrieben, wie wir die Karten erstellen und wie man das selbst machen kann.


