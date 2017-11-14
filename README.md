# PoetryBot
***
A bot to generate poetry in the style of e e cummings.
***
### Overview
This project is intended to test out some cool concepts in language modeling. As development continutes, hopefully we'll get to explore a variety of CL concepts, plus generate some neat poetry along the way.
### who pays any attention to the syntax of things
e e cummings is known for writing expressive but unstructured poetry, often semantically bizarre and with little attention to syntax. Can we generate new poems in the same style?
### General Use
At this stage in development, there are two methods for text generation: **ngram generation** and **part-of-speech generation**. These work as follows:
#### ngram generation
This is a simple n-gram language model. We take a corpus of cummings poetry, consider all bigrams and trigrams, and use that information to generate new text. We begin by choosing a word at random, then choose at random a bigram beginning with that word, and then continue with trigram choices.

For example, we may begin with the word *gone*, chosen randomly. In our training data, we see that *gone* can be followed by *into*, *and*, *to*, and *mouse*. Randomly, we choose *into*. Our poem now reads, "*gone into*."

Now, we look at trigrams beginning with *gone into*. Our options are *gone into vaudeville* and *gone into what*. Randomly, we choose *gone into what*. Our next word will be chosen by looking at trigrams beginning with *into what*, and the process continues accordingly.

A couple of notes:
* **Unknowns** are not an issue for us, since we're only *generating* text from the training corpus (and not *evaluating* new text).
* **Probability** is included in the language model, but as of now it doesn't affect the generated text -- as long as an ngram is possible, it doesn't matter how likely it is. In the future, this may change.
* **Backoff** is used to ensure that new poems are as original as possible. When only **1 trigram** option is found (e.g., the words *into what* only occur once in the corpus, as part of the trigram *into what like*), we resort to **bigram** options (so we would choose from one of the 42 possible words that can *what*).

#### part-of-speech generation
This is a more experimental method in poetry generation. Here, we take existing lines from cummings' poetry and attempt to mirror his unique syntactic structure by replacing each word with a different word of the same part of speech. This is done as follows:
* Before we begin creating our poem, we train a **model for part-of-speech tagging**. This is trained on a large, manually tagged corpus (I use the Brown corpus) and implemented using the Viterbi algorithm.
* To begin generating a new poem, the first step is to choose an **existing cummings poem**, or combine **existing lines** from multiple poems. This gives us the basis for our new poem.
* Second, we **POS-tag** each line in the above using our POS tagger. This gives us a syntactic skeleton to build our new poem around.
* Third, we go through each line and ***replace each word*** with another word from the cummings corpus that can have the same part of speech (according to our POS model). This results in a new poem that is structurally similar to the original cummings work, but completely different in content.

### Some Notes on the Corpora
The corpora used in this project are ["100 Selected Poems"](https://archive.org/stream/100selectedpoems030398mbp/100selectedpoems030398mbp_djvu.txt) of e e cummings, used for the n-gram model and the initial steps of the POS model, and the [Brown corpus](http://www.sls.hawaii.edu/bley-vroman/browntag_nolines.txt) of tagged speech, used for training the POS tagger.
