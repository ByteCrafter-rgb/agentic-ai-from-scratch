- Interesting thing happened on day 2 of this week.
- I asked the model how are you?, but forced the tool use call to get the weather.
- Model did not know which city to extract and present as a arguement to the weather call.
- Now the random city of Pune was chosen two times and its weather was received as answer.
- But in the follow up call to the model , the weather data was ignored as an answer to the orignal greeting that i gave. 
- It is an interesting case.
- Solution to this is let the model decide when to call the tool, by removing AUTO in the configuration.

```the model correctly inferred an implicit need for external data from an indirect question, without you ever mentioning the tool or the word "weather."```