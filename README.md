# Gridcall

### _"Prove you know the grid."_

## The premise

This project is an F1 prediction game where users submit predictions before each race weekend and compete against friends to score the most points over time. 

Before the F1 weekend, users / competitors have to enter their predictions for the results / events of the Race weekend. 

Predictions are organized into objective and subjective categories. 

Users submit the following predictions.

### Objective Predictions
- **Pole Position** — Driver who qualifies P1  
- **Podium** — Drivers who finish P1, P2, and P3  
- **Chaser** — Driver who gains the most positions during the race  

### Subjective Predictions
- **Breakout** — Driver or Team that delivers the biggest positive surprise  
- **Bust** — Driver or Team that delivers the biggest disappointment 

Team predictions score 2x points to encourage higher-risk, higher-reward picks. 

Chaser remains editable until race start, allowing players to react to info such as weather, penalties, or strategic expectations before locking their final call.

Players may go **Full Send** on one prediction. If correct, double points are awarded; Selections lock at race start.

---

## Points system - tentative

### Objective Predictions
- **Pole:** 1 pt  
- **Podium:**  
  - 1 pt for correctly selecting a driver  
  - 2 pts for correctly selecting both the driver and finishing position
- **Chaser:** 1 pt  

### Subjective Predictions
- **Breakout / Bust:**  
  - 1 pt for Driver  
  - 2 pts for Team

---

## Subjective scoring methodology..

Rather than declaring whether a driver or team definitively “was” a Breakout or Bust, the system estimates how likely it is that a reasonable F1 fan would perceive that performance as a big surprise / flop. 

To do this, the model would combine multiple objective signals, including:
- Finishing position relative to car competitiveness
- Qualifying delta vs. teammate
- Grid-to-finish position movement

These signals are treated as inputs to a probabilistic model that outputs a likelihood score. 

Drivers and teams are then ranked by these probabilities, with the top-ranked entries classified as Breakouts and the lowest-ranked as Busts. 

This should reasonably preserve subjectivity by modeling consensus perception rather than enforcing deterministic criteria.
 
The system is designed from the ground up to maintain the user's trust!

---

## Social features

Users can invite friends to their own **Grid** and compete across race weekends to accumulate the most points.

At the end of the day, predictions are more fun when there is someone to make fun of when the picks go wrong.

---

## Goals

- Create an engaging, social F1 prediction experience  
- Balance objective results with subjective interpretation  
- Apply probabilistic modeling to human judgment  
- Maintain transparency and trust in model-driven decisions  

This project is designed to change / evolve over time, with future versions refining the modeling approach as more feedback become available.
