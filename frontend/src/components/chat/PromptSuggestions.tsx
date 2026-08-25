import React from 'react';
import { Compass, RefreshCw, Layers, Sparkles } from 'lucide-react';

interface PromptSuggestionsProps {
  onSelectPrompt: (prompt: string) => void;
}

export const PromptSuggestions: React.FC<PromptSuggestionsProps> = ({ onSelectPrompt }) => {
  const categories = [
    {
      category: 'PRODUCT STRATEGY',
      icon: <Compass className="w-4 h-4 text-amber-500" />,
      color: 'amber',
      prompts: [
        {
          title: 'Deciding What NOT to Build',
          text: 'What does Brian Chesky recommend regarding what NOT to build and founder mode at Airbnb?',
        }
      ]
    },
    {
      category: 'GROWTH LOOPS',
      icon: <RefreshCw className="w-4 h-4 text-blue-500" />,
      color: 'blue',
      prompts: [
        {
          title: 'B2B Growth Loops & PLG',
          text: 'Explain Elena Verna\'s B2B growth loops and how freemium compares to reverse trials.',
        }
      ]
    },
    {
      category: 'PM PRIORITIZATION',
      icon: <Layers className="w-4 h-4 text-emerald-500" />,
      color: 'emerald',
      prompts: [
        {
          title: 'The LNO Framework',
          text: 'How does Shreyas Doshi\'s LNO framework help PMs balance Leverage, Neutral, and Overhead work?',
        }
      ]
    },
    {
      category: 'SHIP 30 FOR 30 SKILL',
      icon: <Sparkles className="w-4 h-4 text-purple-500" />,
      color: 'purple',
      prompts: [
        {
          title: 'Superhuman PMF Engine Essay',
          text: 'Write a Ship 30 for 30 essay on Rahul Vohra\'s 4-step PMF engine and Sean Ellis\'s 40% rule.',
        }
      ]
    }
  ];

  return (
    <div className="flex flex-col items-center justify-center h-full max-w-4xl mx-auto px-6">
      <div className="text-center mb-10 animate-in fade-in slide-in-from-bottom-4 duration-500">
        <h2 className="text-2xl md:text-3xl font-bold text-gray-100 mb-3">
          Turn Lenny's Knowledge into Product Decisions & Artifacts
        </h2>
        <p className="text-sm text-[#94A3B8] max-w-2xl mx-auto leading-relaxed">
          Query hundreds of hours of executive insights from Airbnb, Superhuman, Miro, and Stripe.<br/>
          Get verified, source-grounded answers with instant artifact rendering.
        </p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-4 w-full animate-in fade-in slide-in-from-bottom-6 duration-700">
        {categories.map((cat, idx) => (
          <div key={idx} className="p-4 rounded-xl border border-[#2A3143] bg-[#161B26] hover:bg-[#1A1F2C] transition-colors cursor-pointer group" onClick={() => onSelectPrompt(cat.prompts[0].text)}>
            <div className="flex items-center gap-2 mb-2">
              <div className="p-1.5 rounded-md bg-[#2A3143] group-hover:bg-[#3A435A] transition-colors">
                {cat.icon}
              </div>
              <span className="text-[10px] font-bold tracking-wider text-[#64748B] uppercase">
                {cat.category}
              </span>
            </div>
            <h3 className="text-sm font-bold text-gray-200 mb-1">{cat.prompts[0].title}</h3>
            <p className="text-xs text-[#64748B] group-hover:text-[#94A3B8] transition-colors">
              {cat.prompts[0].text}
            </p>
          </div>
        ))}
      </div>
    </div>
  );
};
