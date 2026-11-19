from src.agents.agents import build_reader_agent, build_search_agent, writer_chain, critic_prompt

def run_research_pipeline(topic: str):

    state = {}

    # Search agent working
    print("\n"+" ="*50)
    print("step1 - search agent in working...")
    print("="*50)

    search_agent = build_search_agent()
    search_result = search_agent.invoke({
        "messages": [("user", f"Find for recent, reliable and detailed information on the topic: {topic}")]
    })

    state["search_results"] = search_result["messages"][-1].content

    print("\n search result ", state['search_results'])


    #step2 - reader agent
    print("\n"+" ="*50)
    print("step2 - reader agent is scraping the resources ...")
    print("="*50)

    reader_agent = build_reader_agent()
    reader_result = reader_agent.invoke({
        "messages": [("user",
                      f"Based on the following search results about '{topic}',"
                      f"Pick the most relevnt URL and scrape it for deeper content.\n\n"
                      f"Search Results:\n{state['search_results'][:800]}"
                      )]

    })

    state["scraped_content"] = reader_result["messages"][-1].content

    print("\n scraped content: \n", state['scraped_content'])

    # step3 - writer chain
    print("\n"+" ="*50)
    print("step3 - writer is drafting the report ...")
    print("="*50)

    research_combined = (
        f"SEARCH RESULTS:\n{state['search_results']}\n\n"
        f"DETAILED SCRAPED CONTENT:\n{state['scraped_content']}"
    )

    state['report'] = writer_chain.invoke({
        "topic": topic,
        "research": research_combined
    })

    print("\n Final Report: \n", state['report'])

    #critic report
    print("\n"+" ="*50)
    print("step4 - Writer drafting a report ...")
    print("="*50)

    state["feedback"] = critic_prompt.invoke({
        "report": state['report']
    })

    print("\n critic report \n", state['feedback'])

    return state


    
    