// Advanced particle system with connections and interactive effects
(function(){
  const root = document.documentElement;
  const canvas = document.createElement('canvas');
  canvas.className = 'fixed inset-0 -z-10';
  canvas.style.pointerEvents = 'none';
  const ctx = canvas.getContext('2d');
  let particles = [];
  const colors = ['#f472b6', '#22d3ee', '#a855f7'];
  const mouse = { x: null, y: null, radius: 150 };

  function resize(){ canvas.width = window.innerWidth; canvas.height = window.innerHeight; }
  window.addEventListener('resize', resize); resize();

  // Track mouse for interactive effects
  window.addEventListener('mousemove', (e) => {
    mouse.x = e.clientX;
    mouse.y = e.clientY;
  });
  
  window.addEventListener('mouseleave', () => {
    mouse.x = null;
    mouse.y = null;
  });

  function spawn(){
    for(let i=0;i<100;i++){
      particles.push({
        x: Math.random()*canvas.width,
        y: Math.random()*canvas.height,
        r: Math.random()*2.2+0.6,
        vx: (Math.random()-0.5)*0.5,
        vy: (Math.random()-0.5)*0.5,
        c: colors[(Math.random()*colors.length)|0],
        a: Math.random()*0.6+0.25,
        phase: Math.random() * Math.PI * 2
      });
    }
  }
  spawn();

  function tick(){
    ctx.clearRect(0,0,canvas.width,canvas.height);
    
    // Draw connections between nearby particles
    for(let i = 0; i < particles.length; i++) {
      for(let j = i + 1; j < particles.length; j++) {
        const dx = particles[i].x - particles[j].x;
        const dy = particles[i].y - particles[j].y;
        const dist = Math.sqrt(dx * dx + dy * dy);
        
        if(dist < 120) {
          ctx.beginPath();
          ctx.strokeStyle = `rgba(244,114,182,${0.12 * (1 - dist / 120)})`;
          ctx.lineWidth = 0.6;
          ctx.moveTo(particles[i].x, particles[i].y);
          ctx.lineTo(particles[j].x, particles[j].y);
          ctx.stroke();
        }
      }
    }
    
    // Update and draw particles
    for(const p of particles){
      // Mouse interaction
      if(mouse.x !== null && mouse.y !== null) {
        const dx = mouse.x - p.x;
        const dy = mouse.y - p.y;
        const dist = Math.sqrt(dx * dx + dy * dy);
        
        if(dist < mouse.radius) {
          const force = (mouse.radius - dist) / mouse.radius;
          p.vx -= (dx / dist) * force * 0.4;
          p.vy -= (dy / dist) * force * 0.4;
        }
      }
      
      p.x += p.vx;
      p.y += p.vy;
      
      // Apply friction
      p.vx *= 0.98;
      p.vy *= 0.98;
      
      // Boundary collision
      if(p.x<0||p.x>canvas.width) {
        p.vx*=-1;
        p.x = p.x < 0 ? 0 : canvas.width;
      }
      if(p.y<0||p.y>canvas.height) {
        p.vy*=-1;
        p.y = p.y < 0 ? 0 : canvas.height;
      }
      
      // Pulsing effect
      p.phase += 0.02;
      const pulse = Math.sin(p.phase) * 0.15 + 1;
      
      // Draw particle with glow
      ctx.beginPath();
      ctx.fillStyle = p.c + Math.floor(p.a*255).toString(16).padStart(2,'0');
      ctx.globalAlpha = p.a;
      ctx.arc(p.x, p.y, p.r * pulse, 0, Math.PI*2);
      ctx.shadowBlur = 12;
      ctx.shadowColor = p.c;
      ctx.fill();
      ctx.shadowBlur = 0;
    }
    ctx.globalAlpha = 1;
    requestAnimationFrame(tick);
  }
  tick();

  document.body.appendChild(canvas);

  // Enhanced 3D tilt effect
  document.querySelectorAll('.tilt').forEach(el=>{
    el.addEventListener('mousemove', (e)=>{
      const r = el.getBoundingClientRect();
      const cx = r.left + r.width/2;
      const cy = r.top + r.height/2;
      const dx = (e.clientX - cx) / r.width;
      const dy = (e.clientY - cy) / r.height;
      el.style.transform = `perspective(1200px) rotateX(${(-dy*8).toFixed(2)}deg) rotateY(${(dx*8).toFixed(2)}deg) scale(1.03) translateZ(15px)`;
      el.style.transition = 'transform 0.1s ease-out';
    });
    el.addEventListener('mouseleave', ()=>{
      el.style.transform = '';
      el.style.transition = 'transform 0.3s ease';
    });
  });
})();

// Agent typing indicator
window.showTypingIndicator = function(containerId) {
  const container = document.getElementById(containerId);
  if (!container) return null;
  
  const bubble = document.createElement('div');
  bubble.id = 'typing-bubble';
  bubble.className = 'bubble ai p-4 rounded-xl mb-3 max-w-2xl pop-in';
  bubble.innerHTML = '<div class="typing-indicator flex gap-1"><span class="w-2 h-2 bg-cyan-400 rounded-full animate-bounce"></span><span class="w-2 h-2 bg-cyan-400 rounded-full animate-bounce" style="animation-delay: 0.2s"></span><span class="w-2 h-2 bg-cyan-400 rounded-full animate-bounce" style="animation-delay: 0.4s"></span></div>';
  container.appendChild(bubble);
  container.scrollTop = container.scrollHeight;
  
  return bubble;
};

window.removeTypingIndicator = function() {
  const bubble = document.getElementById('typing-bubble');
  if (bubble) bubble.remove();
};

// Typewriter effect for AI responses
window.typewriterEffect = function(element, text, speed = 25) {
  element.textContent = '';
  let i = 0;
  return new Promise(resolve => {
    const interval = setInterval(() => {
      if (i < text.length) {
        element.textContent += text.charAt(i);
        i++;
      } else {
        clearInterval(interval);
        resolve();
      }
    }, speed);
  });
};

// Stagger animation helper
window.staggerAnimation = function(selector, animationClass = 'animate-in', delay = 100) {
  document.querySelectorAll(selector).forEach((el, i) => {
    el.classList.add(animationClass);
    el.style.animationDelay = `${i * delay}ms`;
  });
};

// Page load animations
document.addEventListener('DOMContentLoaded', () => {
  staggerAnimation('.stagger-item', 'animate-in', 80);
});
