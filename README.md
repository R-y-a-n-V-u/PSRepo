# Reinforcement Learning Project through the Lens of [Pokémon Showdown](https://pokemonshowdown.com/)

Pokémon Showdown is an open-source battle simulator that turns Pokémon’s turn-based mechanics into a deep, competitive strategy game played by thousands every day. In this environment, battles function as two-player stochastic games with imperfect information: players build teams and make sequential decisions while dealing with uncertainty, hidden information, and randomness. Key aspects of an opponent’s team remain concealed until revealed through gameplay, requiring players to infer missing details, predict strategies, and adapt on the fly. High-level players succeed by anticipating opponents’ actions, managing risk, and maximizing the strengths of their own team. This mix of randomness, partial observability, and immense team diversity makes Pokémon battles a challenging testbed for AI planning, inference, and generalization.

### Table of Contents:
1. Inspiration
2. Data ( scraping + cleaning ) 
3. Base Model Training
4. Training and Evaluation



## Inspiration
Inspired by the [PokeAgent Challenge @ NeurIPS 2025](https://pokeagent.github.io/) and the UT Robot and Perception project [Metamon](https://github.com/UT-Austin-RPL/metamon). We’re using this project as a way to learn reinforce learning through our shared passion of Pokemon Battling and will closely follow the methods of Metamon and other Pokemon battle agents with our own small spins. 

## Data

