# JamBio

Joyful Analysis Management **(JAM)Bio** is a free, open-source, Django-powered data-management app for
performing integrity and quality checks for your Next-Generation Sequencing projects.

Instead of having your sequencing projects *spread* all over the place, you can consolidate them
easily in one place. JamBio sits on a server and allows you to abstract the data
management process through a convenient web-browser.

JamBio also lets you *preserve* the integrity and quality of your sequencing data.
The Transfer app will ensure that the barcodes and sample names you submitted to
the sequencing facility are represented in the FASTQ files you get back - without
having to go through them one by one. Any disparity is clearly highlighted.
The QC app will run FastQC and MultiQC on all your FastQ files and present you
with a report. From this report you'll be able to quickly see if some samples
didn't quite run as expected.

Use JamBio - the time you save is guaranteed to make your colleagues *jelly*.

---

### Installation

If you're using a Ubuntu/Debian, there's a handy [setup script](./setup-debian.sh)
for provisioning your machine once you clone the repo. If not, there aren't too
many dependencies so it shouldn't be too difficult to get it going on other
setups.

To verify the install, just run `python3 manage.py test` and verify everything
is passing.

---

### Usage

The storage scheme is laid out in the apps' `constants.py` module. Essentially,
all your FastQ files should live in their own project folder within
'Project_Storage'. This is where JamBio will go to perform its analyses.

1. The first step should be an integrity check. This can be achieved by filling
out the [sample submission sheet](./JamBio/Sample_Submission_Sheet.xlsx). Once you've
done this, navigate to where you're hosting Jambio and go to *Transfer*. Here
you can upload the aforementioned sample sheet and pick the project folder
containing your FastQ files.

2. If the integrity report looks good, head on over to *QC*, select the same
project and fire it off. The time to completion will depend on the size and
number of FastQ files. You can go to *QC/reports* and click on the project to
see if it's done and view the report.

That's it for now!

---

JamBio is still very much alpha software - but it's being improved all the time!
If you'd like to contribute please fork it and make a pull request.
If you have trouble getting it set up or find bugs, please create an issue!
