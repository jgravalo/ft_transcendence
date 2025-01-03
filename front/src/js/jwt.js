//import jwt_decode from 'jwt-decode';
import jwtDecode from "https://cdn.jsdelivr.net/npm/jwt-decode@latest/build/jwt-decode.esm.js";

export const decodeToken = (token) => {
    try {
        //return jwt_decode(token);
        return jwtDecode(token);
    } catch (error) {
        console.error("Error al decodificar el token:", error);
        return null;
    }
};
