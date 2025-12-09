# Reinforcement Learning Project through the Lens of [Pokémon Showdown](https://pokemonshowdown.com/)

Pokémon Showdown is an open-source battle simulator that turns Pokémon’s turn-based mechanics into a deep, competitive strategy game played by thousands every day. In this environment, battles function as two-player stochastic games with imperfect information: players build teams and make sequential decisions while dealing with uncertainty, hidden information, and randomness. Key aspects of an opponent’s team remain concealed until revealed through gameplay, requiring players to infer missing details, predict strategies, and adapt on the fly. High-level players succeed by anticipating opponents’ actions, managing risk, and maximizing the strengths of their own team. This mix of randomness, partial observability, and immense team diversity makes Pokémon battles a challenging testbed for AI planning, inference, and generalization.

### Table of Contents:
1. Inspiration and Research
2. Data ( scraping + cleaning ) 
3. Base Model Training
4. Training and Evaluation



## Inspiration and Research
Inspired by the [PokeAgent Challenge @ NeurIPS 2025](https://pokeagent.github.io/) and the UT Robot and Perception project [Metamon](https://github.com/UT-Austin-RPL/metamon). We’re using this project as a way to learn reinforce learning through our shared passion of Pokemon Battling and will closely follow the methods of Metamon and other Pokemon battle agents with our own small spins. 

## Research



## Data
Showdown creates "replays" of battles that players can choose to upload to the website before they expire. Our team wanted to build our own data pipeline in order to get hands on experience with the data life cycle within the model development. 


The begining of our Data lifecycle begins with Scraping the Pokemon Showdown website for new battles.
Our [function](data/PS_scraper.py) retrieves recent Generation 9 OU Pokémon Showdown replays and returns only the key information you care about (players, rating, and a direct JSON replay URL).

This brings us to our next step: analyzing the provided JSON files. At first glance, the data contains an overwhelming amount of information—unreadable both to the human eye and to our training agents.
<div align="center">
    <img src="Readme_Media/Example Raw PS data.jpeg" alt="Rawdataexample" width="810">
</div>

<br>

Our next step in the Data pipeline is Cleaning these Files. Our [function](data/PS_json_cleaner.py) takes the raw json file and stripts it of unneccessary information including: Chat messages, Spectator count, and other miscellaneous messages.



Metamon makes it easy to turn Pokémon into an RL research problem by providing over 2m saved datasets.

