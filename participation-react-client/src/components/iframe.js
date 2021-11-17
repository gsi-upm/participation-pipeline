import { useEffect, useState } from "react"

export default function Iframe() {
    const [mobile, setMobile] = useState(false)

    const handleChangeSize = () => {
        setMobile(window.innerWidth < 700)
    }

    useEffect(() => {
        setMobile(window.innerWidth < 700) 
        window.addEventListener('resize', handleChangeSize)
    }, [])

    if (mobile) {
        return (
            // <iframe title="kibana dashboard mobile" src="http://localhost:5601/goto/7d7170773a540105115a9c458f44e9f7"></iframe>
            <iframe title="kibana dashboard mobile" src="http://localhost:5601/goto/42c16ca0cda7b878a3f98af498caa2cd" height="600" width="800"></iframe>
        )
    }

    return (
        // <iframe ref={iframe} src="http://localhost:5601/goto/80deb431eea3a8bf3c42f367de075cad" onLoad={load} style={{height: height.toString() + "px", overflow:'visible'}}></iframe> 
        <iframe title="kibana dashboard" src="http://localhost:5601/goto/42c16ca0cda7b878a3f98af498caa2cd" height="600" width="800"></iframe>
    )
}