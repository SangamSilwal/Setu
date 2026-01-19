import React, { useState, useRef } from 'react';
import { View, Text, TextInput, TouchableOpacity, FlatList, KeyboardAvoidingView, Platform, ActivityIndicator, SafeAreaView } from 'react-native';
import { Send, Scale, User, Menu, MoreVertical } from 'lucide-react-native';
import { apiClient } from '../lib/api-client';
import Markdown from 'react-native-markdown-display';

interface Message {
    id: string;
    role: "user" | "assistant";
    content: string;
    timestamp: Date;
}

export default function ChatScreen() {
    const [messages, setMessages] = useState<Message[]>([
        {
            id: "1",
            role: "assistant",
            content: "Namaste! I am your Nepali Law Assistant. How can I help you today?",
            timestamp: new Date(),
        },
    ]);
    const [input, setInput] = useState("");
    const [isTyping, setIsTyping] = useState(false);
    const flatListRef = useRef<FlatList>(null);

    const handleSend = async () => {
        if (!input.trim()) return;

        const userMsg: Message = {
            id: Date.now().toString(),
            role: "user",
            content: input,
            timestamp: new Date(),
        };

        setMessages((prev) => [...prev, userMsg]);
        const currentInput = input;
        setInput("");
        setIsTyping(true);

        try {
            const response = await apiClient.post<any>("/api/v1/law-explanation/chat", {
                query: currentInput,
                conversation_id: null,
            });

            const formattedContent = response.is_non_legal
                ? response.explanation
                : `### 📝 Summary\n${response.summary}\n\n### 💬 Detailed Explanation\n${response.explanation}\n\n### 🔑 Key Points\n- ${response.key_point}\n\n### 📋 Next Steps\n${response.next_steps}`.trim();

            const assistantMsg: Message = {
                id: (Date.now() + 1).toString(),
                role: "assistant",
                content: formattedContent || "I am having trouble connecting to my legal database.",
                timestamp: new Date(),
            };
            setMessages((prev) => [...prev, assistantMsg]);
        } catch (error) {
            console.error("Chat error:", error);
            const assistantMsg: Message = {
                id: (Date.now() + 1).toString(),
                role: "assistant",
                content: "I encountered an error. Please check your connection to the legal backend.",
                timestamp: new Date(),
            };
            setMessages((prev) => [...prev, assistantMsg]);
        } finally {
            setIsTyping(false);
        }
    };

    return (
        <SafeAreaView className="flex-1 bg-white">
            <KeyboardAvoidingView
                behavior={Platform.OS === "ios" ? "padding" : "height"}
                className="flex-1"
                keyboardVerticalOffset={Platform.OS === "ios" ? 0 : 0}
            >
                {/* Shadcn-style Header */}
                <View className="px-4 py-3 bg-white border-b border-zinc-200 flex-row items-center justify-between">
                    <View className="flex-row items-center">
                        <View className="h-9 w-9 rounded-lg bg-zinc-900 items-center justify-center">
                            <Scale size={20} color="white" />
                        </View>
                        <View className="ml-3">
                            <Text className="text-sm font-semibold text-zinc-900">Law Assistant</Text>
                            <Text className="text-[10px] text-zinc-500 font-medium">AI Powered</Text>
                        </View>
                    </View>
                    <View className="flex-row items-center">
                        <TouchableOpacity className="p-2 mr-1">
                            <MoreVertical size={18} color="#71717a" />
                        </TouchableOpacity>
                        <TouchableOpacity className="p-2">
                            <Menu size={20} color="#71717a" />
                        </TouchableOpacity>
                    </View>
                </View>

                {/* Chat Area */}
                <FlatList
                    ref={flatListRef}
                    data={messages}
                    keyExtractor={(item) => item.id}
                    contentContainerStyle={{ padding: 16, paddingBottom: 32 }}
                    onContentSizeChange={() => flatListRef.current?.scrollToEnd({ animated: true })}
                    renderItem={({ item }) => (
                        <View className={`mb-6 ${item.role === 'user' ? 'items-end' : 'items-start'}`}>
                            <View className={`flex-row ${item.role === 'user' ? 'flex-row-reverse' : ''}`}>
                                {/* Avatar */}
                                <View className={`h-8 w-8 rounded-full items-center justify-center border ${item.role === 'assistant' ? 'bg-zinc-100 border-zinc-200' : 'bg-zinc-900 border-zinc-900'
                                    }`}>
                                    {item.role === 'assistant' ? <Scale size={14} color="#18181b" /> : <User size={14} color="white" />}
                                </View>

                                {/* Bubble */}
                                <View
                                    className={`max-w-[85%] mx-2 p-3 rounded-xl ${item.role === 'user'
                                            ? 'bg-zinc-900'
                                            : 'bg-zinc-50 border border-zinc-200'
                                        }`}
                                >
                                    {item.role === 'assistant' ? (
                                        <Markdown
                                            style={{
                                                body: { color: '#18181b', fontSize: 14, lineHeight: 20 },
                                                heading3: { color: '#09090b', marginTop: 10, marginBottom: 4, fontWeight: '700', fontSize: 15 },
                                                bullet_list: { marginTop: 6 },
                                                list_item: { marginBottom: 4 },
                                                strong: { fontWeight: '700', color: '#09090b' },
                                                paragraph: { marginBottom: 8 }
                                            }}
                                        >
                                            {item.content}
                                        </Markdown>
                                    ) : (
                                        <Text className="text-white text-sm leading-5">
                                            {item.content}
                                        </Text>
                                    )}
                                    <Text className={`text-[9px] mt-1 font-medium ${item.role === 'user' ? 'text-zinc-400 text-right' : 'text-zinc-400'
                                        }`}>
                                        {item.timestamp.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                                    </Text>
                                </View>
                            </View>
                        </View>
                    )}
                />

                {isTyping && (
                    <View className="px-4 py-2 flex-row items-center">
                        <View className="h-8 w-8 rounded-full bg-zinc-100 border border-zinc-200 items-center justify-center mr-2">
                            <Scale size={14} color="#18181b" />
                        </View>
                        <View className="bg-zinc-50 border border-zinc-200 p-2 rounded-xl">
                            <ActivityIndicator size="small" color="#18181b" />
                        </View>
                    </View>
                )}

                {/* Shadcn-style Input Bar */}
                <View className="p-4 bg-white border-t border-zinc-100">
                    <View className="flex-row items-center bg-white rounded-lg border border-zinc-200 px-3 py-1">
                        <TextInput
                            className="flex-1 text-zinc-900 py-2 text-sm"
                            placeholder="Type your legal question..."
                            placeholderTextColor="#a1a1aa"
                            value={input}
                            onChangeText={setInput}
                            multiline
                        />
                        <TouchableOpacity
                            className={`ml-2 h-8 w-8 rounded-md items-center justify-center ${input.trim() ? 'bg-zinc-900' : 'bg-zinc-100'
                                }`}
                            onPress={handleSend}
                            disabled={!input.trim() || isTyping}
                        >
                            <Send size={16} color={input.trim() ? "white" : "#a1a1aa"} />
                        </TouchableOpacity>
                    </View>
                    <Text className="text-[9px] text-center text-zinc-400 mt-3 font-medium">
                        AI-generated content may be inaccurate.
                    </Text>
                </View>
            </KeyboardAvoidingView>
        </SafeAreaView>
    );
}
