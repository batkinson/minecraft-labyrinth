# Minecraft Labyrinth

A program that uses the minecraft pi edition python api to build a game where
the player has to navigate a randomly generated labyrinth to locate treasure
held in a castle.

![Screenshot 1](screenshots/screenshot1.png?raw=true)
![Screenshot 2](screenshots/screenshot2.png?raw=true)
![Screenshot 3](screenshots/screenshot3.png?raw=true)

## Why?

When I found out that there was a simple minecraft version for the raspberry pi,
I wanted to evaluate both what was possible with the API and the relative
difficulty. I found an example online that demonstrated how to build a castle
and adding the labyrinth to turn it into a game added enough complexity to make
it interesting.

The maze generation uses a variant of Prim's spanning tree algorithm, modified
to use vertices rather than edges and uses random selection rather than edge 
weights.

In the end, I was a little disappointed with the quality of minecraft pi edition
and the API due to a number of prominent defects. It was also not easy, complete
nor idiomatic python. As a result, my conclusion was that the game and the API
are too complicated and too limited. If the API was simpler, it could possibly
be used to teach younger students. Additionally, the API doesn't provide enough
functionality to keep more advanced children (or adults) interested.  Given
this, I think there are likely better tools out there to use to teach
programming to younger children.

## Requirements

To run this program, you'll need:

  * A working Python 2 environment
  * A raspberry pi with [minecraft-pi api installed](http://www.raspberrypi-spy.co.uk/2013/10/how-to-setup-minecraft-on-the-raspberry-pi/)

## Running

To run the program, you just need to run:

```
./minecraft_labyrinth.py [host-address] [port]
```

