# Only3000

## Introduction of this folder
The work under this folder is mainly organized by the [2023 Mammoth CupL:DNA storage track](https://micos.cngb.org/zh-hans/) entries. __Only3000__ is the name of our team \(Because the minimum bonus for this competition is 3,000RMB, we are afraid that we will not win anything in the end. However, we did win 3,000 \(before tax\)\).  

Under the __Original\_Work__ folder, I upload the code that my team submitted in the race score. But many of these Settings are specific to this competition. In real DNA storage, it can be a bit more complicated. To this end, I will tidy it up and consider further optimization before uploading it to Github.   

Of course, as for how far to optimize, I still have to discuss the significance of our work with relevant experts. After all, I am not a student in this direction, and I do this work only because I am interested.

## Aim of this work

This is an implementation of a specific __error-correcting code__ \(Substitution + Insertion + Deletion\). The error correction method used is to generate a code table in advance, with a large enough editing distance between each code pair, and then determine the correct one by one-to-one comparison. However, due to the competition period and requirements, we did not give a perfect implementation.  

This work may seem naive, but the results can be amazing. A few days before I was about to participate in the defense, I searched the code table through a refined Levenshtein function and found that a code table with strong performance could exceed the result of the first place. But unfortunately, there were no more running chance at this time. Later, I thought of more optimization methods. If they are all implemented, the performance will be very exciting.  

In this folder, I hope to build a toolkit to serve the related needs of DNA storage.

## Acknowledgement

Thanks to my three teammates for their help in this competition, including but not limited to: programming, coding theory guidance, etc.  

Thanks to __China National GeneBank__ and __Micos Competition__ for providing me with the opportunity to think about this question. And the dedication of the relevant staff.

Thank you for the evaluation of the judges and the wonderful points of the contestants.

\(There may be others to thank......\)
