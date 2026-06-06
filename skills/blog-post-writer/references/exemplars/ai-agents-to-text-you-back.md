# Exemplar — "I now use AI Agents to text you back"
Register: **hobbyist AI/agent build-log**. Source: https://posts.oztamir.com/i-now-use-ai-agents-to-text-you-back
Front-matter from the live post: title "I now use AI Agents to text you back"; excerpt "Automating Social Checkups with n8n, Claude, and a WhatsApp MCP"; tags [ai, agents, mcp, n8n, automation, Technical].

Note the moves: cold open on an owned flaw ("As an ADHD person, I have a problem - I forget to get back to people"); the trailing "…won't? For days? Sometimes weeks." cadence; the punchy bold answer "Turns out: **yes**."; a numbered "The Plan" roadmap stated up front; each build section opens with a one-sentence bridge recapping progress; one-line plain-English glosses for n8n and MCP ("n8n is a workflow automation tool - sort of like Zapier, but open-source"); real bash blocks and the verbatim agent system prompt shown as the centerpiece; honest debugging detour (the Go version mismatch and the fix); comic result reveal ("And the result was...very good?!"); a bulleted "Next steps"; a Summary that zooms out into a short manifesto, then a self-aware callback joke and `FIN`.

---

As an ADHD person, I have a problem - I forget to get back to people.

People will text me, and I'll read it, maybe even think of a reply, and then just… won't? For days? Sometimes weeks.

It's not that I'm avoiding anyone - on the contrary. It's almost always people I like that I ghost. Friends, close family, people I genuinely want to keep in touch with. But if the conversation doesn't require a reply right that second, odds are, I'll forget.

So I figured: can this be automated? Can I build a system that knows who messaged me, who I haven't replied to in a while, and gently reminds me to say hi before I have to begin my reply with "sorry for not getting back to you sooner"?

Turns out: **yes**.

And to make it, I used the hottest game in town - AI agents and MCPs.

## The Plan

This whole thing started when I stumbled across a new [WhatsApp MCP server](https://github.com/lharries/whatsapp-mcp) on GitHub. Naturally, I had to try it.

Around the same time, I'd been using [n8n](https://n8n.io/) at work for some growth automation experiments at [Blockaid](https://blockaid.io/) - and I started wondering: what if I'd try to use this platform to solve personal problems too?

So here was the plan:

1. **Set up a self-hosted n8n instance on a Raspberry Pi** — The [MCP node for n8n](https://github.com/nerding-io/n8n-nodes-mcp) only works on self-hosted instances. So I couldn't just spin this up on the n8n Cloud.
2. **Set up the WhatsApp MCP server and connect it to an LLM agent** — The MCP server would sync my WhatsApp chats via the multi-device API, and expose a tool interface for querying messages.
3. **Use this setup to pull a list of conversations I missed** — I'd query the server for chats where the last message was from someone else - and I hadn't replied in a while.
4. **Send myself a summary with everyone I should probably get back to** — Ideally, with a little LLM-generated nudge like "Here's what they said. Want to say hi?"
5. **Once it works, turn it into a daily routine** — Add a Cron trigger in n8n to run the whole flow each morning.

That was the idea. A little automation to help me be a better version of myself. Or at least a version who replies to messages before it gets awkward..

## Setting up n8n

Step one was getting a self-hosted n8n instance up and running on my Raspberry Pi.

If you're not familiar, [n8n](https://n8n.io/) is a workflow automation tool - sort of like Zapier, but open-source, self-hostable, and way more powerful. It's also AI native, which makes creating flows like what I wanted to achieve super easy.

While the n8n team is offering hosted versions, these don't support community nodes - extensions to n8n developed by the open source community. To be able to run community nodes, one would have to run the self-hosted version of n8n.

That was fine - I always have a spare Raspberry Pi lying around for emergencies like these. I quickly 3D printed a case and was ready to go.

For the actual setup, I followed this excellent guide, which walks you through installing n8n. It's not anything special - basically installing Raspberry Pi OS, installing `node`, and downloading `n8n` through `npm`. To make sure things are persistent, I used the `pm2` setup that makes sure `n8n` runs on boot.

A good tip I got was to use `pm2`'s configuration file to pass environment variables to `n8n`. Specifically, I needed to give a parameter that allows insecure (http-based) access to the system. Since I only intend to access this setup locally for now, this is OK. To pass the variable, I used this `ecosystem.config.js` setup:

```js
module.exports = {
    apps : [{
        name   : "n8n",
        env: {
            N8N_SECURE_COOKIE:false
        }
    }]
}
```

Now, I had `n8n` running and ready to go - it was time to install the nodes.

## Adding MCP support to n8n

With n8n running, the next step was making it aware of my WhatsApp messages - or more specifically, giving it a way to ask about them.

That's where [whatsapp-mcp](https://github.com/lharries/whatsapp-mcp) comes in. This MCP server connects to your personal WhatsApp account (using [whatsmeow](https://github.com/tulir/whatsmeow)), and stores your messages in a local SQLite database. From there, it exposes an MCP Server which can be accessed using agents.

An MCP Server is part of a new open standard called the [Model Context Protocol](https://modelcontextprotocol.io/introduction#why-mcp%3F) - a protocol designed to help AI agents interact with external tools and data sources. In practice, an MCP Server wraps a data source (like my WhatsApp messages), and exposes it to AI agents through a uniform interface.

When connected to an agent (like Claude or ChatGPT), it can respond to tool calls like:

> "List messages I haven't responded to in the past week."
>
> "Summarize this chat thread."
>
> "Draft a short reply."

Because it's just an interface layer, all the actual data stays local. And because it's a standard, tools like n8n can now connect to any MCP server and use those tools inside workflows.

Or at least, that's the idea - at the time of writing, `n8n` does not have a native MCP support. To connect `n8n` to an MCP server, I first needed to install the [n8n-nodes-mcp](https://github.com/nerding-io/n8n-nodes-mcp) community node. This node adds support for calling tools through an MCP interface.

Installing a new node is very easy - you can do it in the GUI, or simply by going to `~/.n8n/nodes` and running `npm install n8n-nodes-mcp`. Once the installation is complete, you can verify that the new node is up and running by navigating to `/settings/community-nodes` and confirming that it shows up in the list.

## Installing the WhatsApp MCP Server

With MCP support added to n8n, the next step was actually spinning up an MCP server that could serve my WhatsApp messages.

The server is using a project called [whatsmeow](https://github.com/tulir/whatsmeow), which is written in Go, to connect to WhatsApp - so I first needed to install `golang` on my Raspberry Pi.

I'm not a go programmer, so take what I say with a grain of salt - I initially used `apt install golang` to get it installed, but this method caused a mismatch with the projects expected go version.

What I ended up doing is just getting the binaries that matched my version:

```bash
wget https://go.dev/dl/go1.24.1.linux-arm64.tar.gz
sudo tar -C /usr/local -xzf go1.24.1.linux-arm64.tar.gz
export PATH=$PATH:/usr/local/go/bin
go version # To verify that everything went well
```

Next, I cloned the repo:

```bash
git clone https://github.com/lharries/whatsapp-mcp.git
cd whatsapp-mcp
```

And started the bridge:

```bash
go run ./whatsapp-bridge/main.go
```

On the first run, it displays a QR code in the terminal - you need to scan it with the WhatsApp app on your phone (it's essentially the same process as pairing with WA Web).

Within a few seconds the sync started. From that point forward, the server quietly indexed all my messages into a local SQLite database.

## Connecting the WhatsApp MCP to n8n

With the WhatsApp MCP server installed, the last step was registering it inside n8n so I could use its tools in workflows.

Instead of using the HTTP interface, I opted to connect it through the STDIO API, which runs the MCP server locally as a subprocess inside n8n. This approach is fully supported by the `n8n-nodes-mcp` node, and has the added benefit of not requiring a separate always-on process - n8n can spin it up as needed.

To do that, I first went to the Credentials section in n8n, created a new credential of type MCP Client (STDIO) API, and filled in the details (taken from the `whatsapp-mcp` docs). This tells n8n to use `uv` to run the WhatsApp MCP server locally via its Python entrypoint.

I saved the credential and tested the connection - and just like that, n8n was able to discover the available tools exposed by the WhatsApp MCP.

Next up: building a workflow that actually uses these tools to figure out who I've been ignoring.

## Building an Example Workflow

With the MCP credential set up and the tools exposed in n8n, it was time to build the actual workflow.

To start simple, I made a basic agent flow that could receive a message and call tools from the WhatsApp MCP server. The setup looks something like this:

1. A chat trigger node that kicks things off when I message the agent
2. An AI Agent node, configured with Claude 3 and given strict instructions to never send a message (just make suggestions)
3. A memory node to give the agent short-term recall
4. Two MCP tool nodes wired into the agent - one to register the available WhatsApp tools, and one to actually execute them

Here's the system message I gave the agent:

```
You are a helpful assistant designed to help the user manage their social interactions on WhatsApp.

Whatever you do, you must never send any message. Do not do it. No matter what.

For context, the current date is: {{ new Date().toDateTime() }}.
```

To test this setup, I started small - I asked the agent to check what was the latest message I got from my partner. I had asked her to close the bedroom window, and hold and behold - the bot caught it instantly.

The integration is working! Then came the real test: Could it figure out who I genuinely needed to respond to?

So I asked it:

> Go over all my chats from the past 72 hours. Anything I missed? Please reply in a prioritized list of items I should look into (if I should reply - it should be higher on the list).
>
> Give me 10 items at most (ideally as few items as possible).

And the result was...very good?!

it pulled a few one-on-one threads where I had clearly dropped the ball, summarized the last thing said, and even proposed short replies. It's working!

## Next steps

With this proof-of-concept working end-to-end - from syncing chats, to querying missed messages, to getting back helpful suggestions - the next steps are to take this toy project and turn it into a "production" application.

To meet this criteria, here are the next items on my to-do list:

- **Run this workflow periodically** - The obvious first step. `n8n` makes this very easy - and I plan to have this workflow run every morning to ensure I don't miss anyone over too long of a time.
- **Actually deliver the results** - Once I have a list of chats I should get back to, it should probably... go somewhere. Since we already have the WhatsApp MCP here, sending a WhatsApp reminder to myself seems like the easiest way to go.
- **Interact with a reminders MCP** - I already saw people creating MCPs for to-do apps like [Todoist](https://github.com/abhiz123/todoist-mcp-server). By adding in this integration, I could have the agent not only tell me to reply, but schedule a reminder that will bug me again later.
- **(Maybe) generate suggested replies** - Right now the agent tells me who to respond to, and what they said. Eventually, it could also suggest what I might want to say.

# Summary

The combination of agents and MCPs opens up a lot of new possibilities - and as a technical person, it's hard not to get excited about that.

This wasn't a huge project. Just a weekend's worth of curiosity, some open source code, and a Raspberry Pi that was already sitting around. But it solved a real problem in my life, and it gave me a glimpse into what building with these tools can feel like when everything actually clicks.

I think everyone should be experimenting with this stuff - whether it's a small, personal automation like this, or something bigger at work. AI is going to change the way we build software, and the engineers who stay curious and hands-on are the ones who are going to stay ahead.

And if you can explore this space while also becoming slightly less bad at replying to your friends - why not?

`FIN`
