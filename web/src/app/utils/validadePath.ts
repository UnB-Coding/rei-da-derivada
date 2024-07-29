export default function validatePath(role: string, path: string): boolean{
    let ans: boolean = false;
    const adminpaths = ["admin", "sumula", "results"];
    const staffpaths = ["sumula", "results"];
    const playerpaths = ["profile", "results"];
    if(role === "admin" || role === "manager"){
        adminpaths.includes(path) ? ans = true : ans = false;
    } else if (role === "staff"){
        staffpaths.includes(path) ? ans = true : ans = false;
    } else {
        playerpaths.includes(path) ? ans = true : ans = false;
    }
    return ans;
}
