# Bus Buzz
`Taking a bus? Check BusBuzz - a mobile app that buzzes you the current location and expected head count in your bus`

## Inspiration
### Scene 1
You are standing at a bus stop after you saw on Google Maps that it is supposed to reach in the next 5 minutes. You reach after 2 minutes and you are now unsure whether the bus has already passed or is yet to come. 

### Scene 2
You are standing at a bus stop waiting for a bus to take you to your favorite place. You are still waiting.  When the bus finally arrives, the number of people on the bus is equal to the number of people downloading GoT from Torrents the nanosecond it released. 
You are in a dilemma whether to enter this bus or wait for the next bus to arrive. Even if you wait, you don't know how full the next bus would be. 

### Scene 3
You finally enter the bus. The conductor comes and asks you to give him Rs.13 for your trip. After fidgeting for 5 minutes with your wallet you finally give him a Rs. 20 note. He gives you the ticket with a big 7 written on it and a weird smile. You most likely forget to take your change back when you get down. 

## What it does
**Bus Buzz** draws ideas heavily from the concept of Bit Torrent, i.e. You need to seed if you wish to leech. It is a crowd-sourced application which provides accurate and reliable local bus arrival schedule and its occupancy information. 

The application homepage allows you to search for buses on the route you wish to travel. The moment you enter the bus, BusBuzz starts sending your location information to our central server till the time you offboard. The geocoding information received from your phone will help BusBuzz in predicting times accurately for others waiting to board the bus. The number of people transferring information from a particular bus also makes it a reliable source of finding the bus occupancy. 

BusBuzz integrates seamlessly with payment applications for a cashless and seamless payment experience.  

On top of this, BusBuzz provides some interesting analytics, incredibly useful for advertisers and government bodies too. 

## How we built it

We used Python-flask as our backend and semantic-ui for frontend. We use postgres as our database. We extensively used the Google Maps API and bus schedule information was received from https://narsimhadutta.com. 

## Challenges we ran into
Since the application relies on geolocation for accurate predictions, we could not test our application. We had to create scripts to artificially mock geo-coordinates and show various passengers boarding the buses to verify if our product works! 

The project is a distributed system. Synchronization of various devices connecting to the server was difficult as it led to race conditions often. 

## Accomplishments that we're proud of
We have a fully working demo with a seamless UI. It is an application we ourselves would be using. As early as when this hackathon ends and we head home! 

## What we learned
Integration with Google Maps, flask services, understanding the importance of a database wrapper and a lot of high speed, caffeinated coding experience!

## What's next for Bus Buzz
We don't see Bus Buzz as a project limited to only this hackathon. It has a lot of value in the real world and is solving a problem a lot of us face. With some proper guidance, we could transmute Bus Buzz into a useful utility for everyone using the public transport system