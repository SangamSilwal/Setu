import AsyncStorage from '@react-native-async-storage/async-storage';

/**
 * Authentication utility functions for managing tokens and user data in AsyncStorage
 */

export const AUTH_KEYS = {
    ACCESS_TOKEN: "access_token",
    REFRESH_TOKEN: "refresh_token",
    USER: "user",
} as const

/**
 * Store authentication data in AsyncStorage
 */
export async function setAuthData(accessToken: string, refreshToken?: string, user?: any) {
    await AsyncStorage.setItem(AUTH_KEYS.ACCESS_TOKEN, accessToken)

    if (refreshToken) {
        await AsyncStorage.setItem(AUTH_KEYS.REFRESH_TOKEN, refreshToken)
    }

    if (user) {
        await AsyncStorage.setItem(AUTH_KEYS.USER, JSON.stringify(user))
    }
}

/**
 * Get access token from AsyncStorage
 */
export async function getAccessToken(): Promise<string | null> {
    return await AsyncStorage.getItem(AUTH_KEYS.ACCESS_TOKEN)
}

/**
 * Get refresh token from AsyncStorage
 */
export async function getRefreshToken(): Promise<string | null> {
    return await AsyncStorage.getItem(AUTH_KEYS.REFRESH_TOKEN)
}

/**
 * Get user data from AsyncStorage
 */
export async function getUser(): Promise<any | null> {
    const userStr = await AsyncStorage.getItem(AUTH_KEYS.USER)
    if (!userStr) return null

    try {
        return JSON.parse(userStr)
    } catch {
        return null
    }
}

/**
 * Clear all authentication data from AsyncStorage
 */
export async function clearAuthData() {
    await AsyncStorage.removeItem(AUTH_KEYS.ACCESS_TOKEN)
    await AsyncStorage.removeItem(AUTH_KEYS.REFRESH_TOKEN)
    await AsyncStorage.removeItem(AUTH_KEYS.USER)
}

/**
 * Check if user is authenticated (has valid access token)
 */
export async function isAuthenticated(): Promise<boolean> {
    const token = await getAccessToken()
    return token !== null
}
