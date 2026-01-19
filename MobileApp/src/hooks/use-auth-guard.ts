import { useEffect } from "react"
import { useNavigation } from "@react-navigation/native"
import { useAuth } from "../context/AuthContext"

/**
 * Hook to protect screens that require authentication
 */
export function useAuthGuard() {
    const navigation = useNavigation<any>()
    const { isAuth, isLoading } = useAuth()

    useEffect(() => {
        if (!isLoading && !isAuth) {
            navigation.navigate("Login")
        }
    }, [isAuth, isLoading, navigation])

    return { isLoading, isAuthenticated: isAuth }
}
