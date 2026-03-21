import { useEffect, useState } from 'react'

export default function BackgroundStars() {
  const [stars, setStars] = useState([])
  const [shootingStars, setShootingStars] = useState([])

  useEffect(() => {
    // 80 stars with varying brightness and sizes
    const newStars = Array.from({ length: 80 }).map((_, i) => {
      const isBright = Math.random() > 0.85; // 15% are distinctly bright "cross" stars
      return {
        id: i,
        left: `${Math.random() * 100}%`,
        top: `${Math.random() * 100}%`,
        size: isBright ? `${Math.random() * 1.5 + 1.5}px` : `${Math.random() * 1 + 0.5}px`, // pinpoints of light
        isBright,
        animationDelay: `${Math.random() * 5}s`,
        animationDuration: `${Math.random() * 4 + 3}s`,
      };
    })
    setStars(newStars)

    // 6 slightly more frequent shooting stars
    const newShootingStars = Array.from({ length: 6 }).map((_, i) => ({
      id: `shoot-${i}`,
      left: `${Math.random() * 80}%`, 
      top: `${Math.random() * 50}%`,  // start in the upper half mostly
      delay: `${Math.random() * 8}s`,
      duration: `${Math.random() * 6 + 10}s`, // 10 to 16 seconds cycle
    }))
    setShootingStars(newShootingStars)
  }, [])

  return (
    <div className="stars-container">
      {stars.map(star => (
        <div 
          key={star.id} 
          className={`star ${star.isBright ? 'bright-star' : ''}`} 
          style={{
            left: star.left,
            top: star.top,
            width: star.size,
            height: star.size,
            animationDelay: star.animationDelay,
            animationDuration: star.animationDuration,
          }}
        />
      ))}
      {shootingStars.map(star => (
        <div 
          key={star.id} 
          className="shooting-star" 
          style={{
            left: star.left,
            top: star.top,
            animationDelay: star.delay,
            animationDuration: star.duration,
          }}
        />
      ))}
    </div>
  )
}
