import { useState, useRef, useEffect } from 'react'
import { motion, useInView } from 'framer-motion'

const CYPHERS = "ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789@#X%&*"

export default function TerminalText({ text, delay = 0 }) {
  const ref = useRef(null)
  const isInView = useInView(ref, { once: true, margin: "-10px" })
  const [displayText, setDisplayText] = useState(text.replace(/[a-zA-Z0-9]/g, '█'))

  useEffect(() => {
    if (!isInView) return
    let iteration = 0
    let interval = null
    const t = setTimeout(() => {
      interval = setInterval(() => {
        setDisplayText(
          text.split("").map((letter, index) => {
            if (index < iteration) return text[index]
            if (letter === " " || letter === "," || letter === ".") return letter
            return CYPHERS[Math.floor(Math.random() * CYPHERS.length)]
          }).join("")
        )
        if (iteration >= text.length) clearInterval(interval)
        iteration += 1 / 2 // Speed of decryption
      }, 30)
    }, delay * 1000)

    return () => { clearTimeout(t); clearInterval(interval) }
  }, [isInView, text, delay])

  return <span ref={ref}>{displayText}</span>
}
