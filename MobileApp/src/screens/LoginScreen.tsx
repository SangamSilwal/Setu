import React, { useState } from 'react';
import { View, Text, TextInput, TouchableOpacity, ActivityIndicator, KeyboardAvoidingView, Platform, ScrollView, SafeAreaView } from 'react-native';
import { useAuth } from '../context/AuthContext';
import { Scale, Mail, Lock, ArrowRight } from 'lucide-react-native';

export default function LoginScreen() {
    const [email, setEmail] = useState("");
    const [password, setPassword] = useState("");
    const [error, setError] = useState<string | null>(null);
    const [isLoading, setIsLoading] = useState(false);
    const { login } = useAuth();

    const handleLogin = async () => {
        if (!email || !password) {
            setError("Please fill in all fields");
            return;
        }

        setError(null);
        setIsLoading(true);

        try {
            await login(email, password);
        } catch (err) {
            setError(err instanceof Error ? err.message : "Invalid email or password");
        } finally {
            setIsLoading(false);
        }
    };

    return (
        <SafeAreaView className="flex-1 bg-white">
            <KeyboardAvoidingView
                behavior={Platform.OS === "ios" ? "padding" : "height"}
                className="flex-1"
            >
                <ScrollView contentContainerStyle={{ flexGrow: 1 }} className="px-6">
                    <View className="flex-1 justify-center py-10">
                        {/* Shadcn-style Header */}
                        <View className="items-center mb-10">
                            <View className="h-12 w-12 rounded-xl bg-zinc-900 items-center justify-center mb-4">
                                <Scale size={28} color="white" />
                            </View>
                            <Text className="text-2xl font-bold text-zinc-900">Welcome back</Text>
                            <Text className="text-zinc-500 text-sm mt-1">Enter your credentials to access your account</Text>
                        </View>

                        {/* Form */}
                        <View className="space-y-4">
                            <View>
                                <Text className="text-sm font-medium text-zinc-900 mb-1.5 ml-0.5">Email</Text>
                                <View className="flex-row items-center bg-white border border-zinc-200 rounded-lg px-3 py-3">
                                    <Mail size={18} color="#71717a" />
                                    <TextInput
                                        className="flex-1 ml-2.5 text-zinc-900 text-sm"
                                        placeholder="m@example.com"
                                        placeholderTextColor="#a1a1aa"
                                        value={email}
                                        onChangeText={setEmail}
                                        autoCapitalize="none"
                                        keyboardType="email-address"
                                    />
                                </View>
                            </View>

                            <View className="mt-4">
                                <View className="flex-row justify-between items-center mb-1.5 ml-0.5">
                                    <Text className="text-sm font-medium text-zinc-900">Password</Text>
                                    <TouchableOpacity>
                                        <Text className="text-xs text-zinc-500 underline">Forgot password?</Text>
                                    </TouchableOpacity>
                                </View>
                                <View className="flex-row items-center bg-white border border-zinc-200 rounded-lg px-3 py-3">
                                    <Lock size={18} color="#71717a" />
                                    <TextInput
                                        className="flex-1 ml-2.5 text-zinc-900 text-sm"
                                        placeholder="••••••••"
                                        placeholderTextColor="#a1a1aa"
                                        value={password}
                                        onChangeText={setPassword}
                                        secureTextEntry
                                    />
                                </View>
                            </View>

                            {error && (
                                <View className="bg-red-50 p-3 rounded-lg border border-red-100 mt-4">
                                    <Text className="text-red-600 text-xs font-medium text-center">{error}</Text>
                                </View>
                            )}

                            <TouchableOpacity
                                className={`mt-6 h-11 rounded-lg flex-row items-center justify-center ${isLoading ? 'bg-zinc-800' : 'bg-zinc-900'
                                    }`}
                                onPress={handleLogin}
                                disabled={isLoading}
                            >
                                {isLoading ? (
                                    <ActivityIndicator color="white" size="small" />
                                ) : (
                                    <Text className="text-white font-semibold text-sm">Sign In</Text>
                                )}
                            </TouchableOpacity>

                            <View className="flex-row items-center my-6">
                                <View className="flex-1 h-[1px] bg-zinc-200" />
                                <Text className="mx-4 text-[10px] text-zinc-400 font-bold uppercase tracking-widest">Or continue with</Text>
                                <View className="flex-1 h-[1px] bg-zinc-200" />
                            </View>

                            <TouchableOpacity className="h-11 border border-zinc-200 rounded-lg items-center justify-center bg-white">
                                <Text className="text-zinc-900 font-medium text-sm">Google</Text>
                            </TouchableOpacity>
                        </View>

                        {/* Footer */}
                        <View className="mt-10 items-center">
                            <Text className="text-zinc-500 text-xs">
                                Don't have an account? <Text className="text-zinc-900 font-bold underline">Sign up</Text>
                            </Text>
                        </View>
                    </View>
                </ScrollView>
            </KeyboardAvoidingView>
        </SafeAreaView>
    );
}
