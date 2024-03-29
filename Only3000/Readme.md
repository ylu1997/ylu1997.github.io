# 2023 "Mammoth Cup" International Contest on Omics Sciences

## Introduction of this folder
The work under this folder is mainly for the [2023 Mammoth Cup:DNA storage track](https://micos.cngb.org/zh-hans/)  [(English Version)](https://micos.cngb.org/en/). __Only3000__ is the name of our team \(Because the minimum bonus for this competition is 3,000RMB, we are afraid that we will not win anything in the end. However, we did win 3,000 \(before tax\)\). 

### Our Team
[Chenghao Li](https://scholar.google.com/citations?user=fBmz2LsAAAAJ&hl=zh-CN), [Yi Lu](https://ylu1997.github.io/), Yun Ma, Xin Zhang


<!-- In the __Original\_Work__ folder, I upload the code that my team submitted in the race. But many of these Settings are specific to this competition. In real DNA storage, it can be a bit more complicated. I will tidy it up and consider further optimization for it.    -->

## Technical document

Technical documentation can be found [here](https://ylu1997.github.io/Only3000/dnapdf.pdf)

Principle of Refined Levenshtein Function can be found [here](https://ylu1997.github.io/Only3000/Refined_Levenshtein.pdf)
## Code(TBC)

This is an implementation of a specific __error-correcting code__ \(Substitution + Insertion + Deletion\) with restriction of runs and balance. The error correction method used is to generate a code table in advance, with a large enough editing distance between each code pair, and then determine the correct one by one-to-one comparison. However, due to the competition period and requirements, we did not give a perfect implementation.  

This work may seem naive, but the results can be amazing. A few days before I was about to participate in the defense, I searched the code table through a refined Levenshtein function and found that a code table with strong performance could exceed the result of the first place. But unfortunately, there were no more running chance at this time. Later, I thought of more optimization methods. If they are all implemented, the performance will be very exciting.  

In this folder, I hope to build a toolkit to serve the related needs of DNA storage.

For a more comprehensive solution, please refer to [The Scheme of Codebook Generation](https://github.com/ylu1997/Code_Generation_For_DNA_Storage) for future work.

## Result

After rigorous evaluation and selection through the preliminary and semi-final rounds, our team, along with 21 others, emerged from over **400** participating teams to enter the final showdown. Following intense competition, we achieved an impressive **7th** place in the DNA track!

Officially result can be found at [WeChat](https://mp.weixin.qq.com/s/xq53KaUbMAaSAgBOdpPBeg)

<img src="Original_Work/dnatrack_all.png" alt="result" width="1000" height="600">

## Acknowledgement

Thanks to __China National GeneBank__ and __Micos Competition__ for providing me with the precious opportunity to communicate with professors and other players.  

Thanks to my three teammates for their help in this competition, including but not limited to: programming, coding theory guidance, etc.   

Thanks to the staff of this competition for their contributions for this competition.  

Thanks to the professors for their comments and the players for their wonderful presentations.  

\(There may be others to thank......\)

## Disclaimer

The contents within this folder are intended solely for educational and research purposes.

Any consequences arising from practical applications are not the responsibility of the undersigned.


Yi Lu.

