## 6. React Conversation State

### useReducer for Complex Chat State

```typescript
interface ConversationState {
  readonly messages: Message[];
  readonly isStreaming: boolean;
  readonly agentState: AgentState;
  readonly suggestedReplies: SuggestedReply[];
  readonly error: string | null;
  // Side-effect flags (processed by useEffect)
  readonly shouldInvalidateQuery: boolean;
}

type ConversationAction =
  | { type: "START_STREAMING" }
  | { type: "PROCESS_SSE_EVENT"; payload: ChatEvent }
  | { type: "STREAMING_COMPLETE" }
  | { type: "CLEAR_SIDE_EFFECT_FLAGS" };

function conversationReducer(
  state: ConversationState,
  action: ConversationAction,
): ConversationState {
  switch (action.type) {
    case "PROCESS_SSE_EVENT": {
      const event = action.payload;
      let newState = state;

      // Update agent state via sub-reducer
      newState = {
        ...newState,
        agentState: reduceAgentState(state.agentState, event),
      };

      // Handle text streaming
      if (event.type === "TEXT_MESSAGE_CONTENT") {
        const lastMsg = newState.messages[newState.messages.length - 1];
        if (lastMsg?.role === "assistant") {
          newState = {
            ...newState,
            messages: [
              ...newState.messages.slice(0, -1),
              { ...lastMsg, content: lastMsg.content + event.delta },
            ],
          };
        }
      }

      // Handle structured suggested_replies (from CUSTOM event)
      if (
        event.type === "CUSTOM" &&
        event.custom_type === "suggested_replies"
      ) {
        newState = {
          ...newState,
          suggestedReplies: event.custom_data?.replies ?? [],
        };
      }

      return newState;
    }
    // ... other cases
  }
}
```

### Context Provider with Side Effects

```typescript
function ConversationProvider({ children }: { children: React.ReactNode }) {
  const [state, dispatch] = useReducer(conversationReducer, INITIAL_STATE);
  const queryClient = useQueryClient();

  // Handle side effects via flags (not in reducer)
  useEffect(() => {
    if (state.shouldInvalidateQuery) {
      queryClient.invalidateQueries({ queryKey: ["conversation"] });
      dispatch({ type: "CLEAR_SIDE_EFFECT_FLAGS" });
    }
  }, [state.shouldInvalidateQuery, queryClient]);

  return (
    <ConversationContext.Provider value={{ state, dispatch }}>
      {children}
    </ConversationContext.Provider>
  );
}
```

### SSE Event Processing Hook

```typescript
function useSSEStream(conversationId: string) {
  const { dispatch } = useConversation();
  const abortRef = useRef<AbortController | null>(null);

  const sendMessage = useCallback(
    async (message: string) => {
      abortRef.current = new AbortController();
      dispatch({ type: "START_STREAMING" });

      try {
        const response = await fetch(`/api/chat/${conversationId}`, {
          method: "POST",
          body: JSON.stringify({ message }),
          signal: abortRef.current.signal,
        });

        const reader = response.body!.getReader();
        const decoder = new TextDecoder();

        while (true) {
          const { done, value } = await reader.read();
          if (done) break;

          const text = decoder.decode(value);
          for (const line of text.split("\n")) {
            if (line.startsWith("data: ")) {
              const event = JSON.parse(line.slice(6));
              dispatch({ type: "PROCESS_SSE_EVENT", payload: event });
            }
          }
        }
      } finally {
        dispatch({ type: "STREAMING_COMPLETE" });
      }
    },
    [conversationId, dispatch],
  );

  return { sendMessage };
}
```

---

