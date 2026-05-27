export interface Feature {
  id: string;
  title: string;
  description: string;
  details: {
    fullDescription: string;
    highlights: string[];
    relatedSessions?: string[];
  };
}

export const FEATURES: Feature[] = [
  {
    id: 'technical-deep-dives',
    title: 'Technical Deep Dives',
    description: 'Get hands-on with the latest LLMs and neural architectures.',
    details: {
      fullDescription: 'Our technical deep dives are immersive sessions designed for engineers and researchers who want to understand the nuts and bolts of modern AI. Led by the creators of popular frameworks and models, these sessions go beyond the surface level.',
      highlights: [
        'Live coding sessions with PyTorch and TensorFlow core developers.',
        'Architecture breakdowns of GPT-4, Llama 3, and Gemini.',
        'Optimization techniques for training and inference at scale.',
        'Debugging and interpretability workshops.'
      ]
    }
  },
  {
    id: 'industry-networking',
    title: 'Industry Networking',
    description: 'Connect with leaders from top tech companies and startups.',
    details: {
      fullDescription: 'Networking is at the heart of the AI Summit. We facilitate structured and unstructured opportunities for you to meet peers, mentors, and potential collaborators. Whether you are looking for a co-founder, a job, or just intellectual stimulation, this is the place.',
      highlights: [
        'Speed networking sessions matched by interest.',
        'VIP receptions for industry leaders.',
        'Community lounges for specific domains (Healthcare, Finance, etc.).',
        'app-based matchmaking.'
      ]
    }
  },
  {
    id: 'research-papers',
    title: 'Research Papers',
    description: 'First look at groundbreaking papers before they hit ArXiv.',
    details: {
      fullDescription: 'Stay ahead of the curve with our exclusive research track. We feature paper presentations from top labs including OpenAI, DeepMind, FAIR, and major universities. Many of these works are being presented to the public for the first time.',
      highlights: [
        'Poster sessions with direct access to authors.',
        'Panel discussions on the future of research directions.',
        'Best Paper Awards ceremony.',
        'Workshops on writing and publishing in top conferences.'
      ]
    }
  },
  {
    id: 'career-growth',
    title: 'Career Growth',
    description: 'Workshops designed to accelerate your career in AI.',
    details: {
      fullDescription: 'The AI job market is evolving rapidly. Our career growth track provides actionable advice on navigating this landscape, from negotiation strategies to technical interview prep and leadership skills for engineering managers.',
      highlights: [
        'Resume reviews by recruiters from top tech firms.',
        'Mock interview sessions.',
        'Talks on transitioning from IC to Management.',
        'Salary negotiation workshops.'
      ]
    }
  },
  {
    id: 'expo-hall',
    title: 'Expo Hall',
    description: 'Demo the newest tools and platforms in the AI ecosystem.',
    details: {
      fullDescription: 'The Expo Hall is a playground for AI enthusiasts. Discover the latest MLOps tools, hardware accelerators, and cloud platforms. Engage with vendors, get hands-on demos, and collect some amazing swag.',
      highlights: [
        'Over 100 exhibitors from startups to tech giants.',
        'Startup Alley featuring the most promising new companies.',
        'Hardware petting zoo (GPUs, TPUs, and Robotics).',
        'Live product launches.'
      ]
    }
  },
  {
    id: 'social-events',
    title: 'Social Events',
    description: 'Unwind at our legendary after-parties and mixers.',
    details: {
      fullDescription: 'All work and no play makes for a dull conference. Our social events are legendary. From the welcome reception to the closing party, enjoy great food, music, and company in some of San Francisco\'s most iconic venues.',
      highlights: [
        'Opening Night Welcome Reception.',
        'The "AI Prom" (formal attire optional).',
        'Hackathon after-party.',
        'Morning yoga and run clubs.'
      ]
    }
  }
];
