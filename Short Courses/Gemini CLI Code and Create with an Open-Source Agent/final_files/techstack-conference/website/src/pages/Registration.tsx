import { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Check, ArrowLeft, Loader2, CreditCard, User, Building, Mail, Utensils } from 'lucide-react';
import { useNavigate } from 'react-router-dom';

interface Tier {
  name: string;
  price: string;
  description: string;
  features: string[];
  popular?: boolean;
}

export const Registration = () => {
  const navigate = useNavigate();
  const [step, setStep] = useState<'selection' | 'form' | 'success'>('selection');
  const [selectedTier, setSelectedTier] = useState<Tier | null>(null);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [formData, setFormData] = useState({
    firstName: '',
    lastName: '',
    email: '',
    company: '',
    jobTitle: '',
    dietary: '',
    tshirt: 'L',
  });

  const handleSelectTier = (tier: Tier) => {
    setSelectedTier(tier);
    setStep('form');
    window.scrollTo({ top: 0, behavior: 'smooth' });
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsSubmitting(true);
    // Simulate API call
    await new Promise(resolve => setTimeout(resolve, 1500));
    setIsSubmitting(false);
    setStep('success');
    window.scrollTo({ top: 0, behavior: 'smooth' });
  };

  const containerVariants = {
    hidden: { opacity: 0 },
    visible: {
      opacity: 1,
      transition: {
        staggerChildren: 0.1
      }
    },
    exit: { opacity: 0, y: -20, transition: { duration: 0.2 } }
  };

  const itemVariants = {
    hidden: { opacity: 0, y: 20 },
    visible: { opacity: 1, y: 0 }
  };

  const tiers = [
    {
      name: "Explorer",
      price: "$99",
      description: "Perfect for students and hobbyists.",
      features: ["Access to Keynotes", "Expo Hall Entry", "Networking App", "Conference Swag"]
    },
    {
      name: "Innovator",
      price: "$199",
      popular: true,
      description: "The full conference experience.",
      features: ["All Keynotes & Breakouts", "Workshops & Labs", "Lunch & Refreshments", "Summit Party Ticket", "Session Recordings"]
    },
    {
      name: "Visionary",
      price: "$499",
      description: "VIP access and exclusive perks.",
      features: ["VIP Seating", "Executive Lounge Access", "Private Speaker Meetups", "Gala Dinner Invite", "Concierge Service", "Everything in Innovator"]
    }
  ];

  return (
    <div className="min-h-screen py-24 bg-slate-50 dark:bg-slate-950">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        
        <AnimatePresence mode="wait">
          {step === 'selection' && (
            <motion.div 
              key="selection" 
              variants={containerVariants}
              initial="hidden"
              animate="visible"
              exit="exit"
            >
              <motion.div variants={itemVariants} className="text-center mb-16">
                <h2 className="text-3xl font-bold text-slate-900 dark:text-white mb-4">Registration Packages</h2>
                <p className="text-slate-600 dark:text-slate-400">Choose the perfect pass for your summit experience.</p>
              </motion.div>

              <div className="grid md:grid-cols-3 gap-8">
                {tiers.map((tier) => (
                  <motion.div
                    key={tier.name}
                    variants={itemVariants}
                    className={`relative p-8 rounded-2xl border ${tier.popular ? 'border-primary-500 ring-2 ring-primary-500/20' : 'border-slate-200 dark:border-slate-800'} bg-white dark:bg-slate-900 flex flex-col shadow-sm hover:shadow-lg transition-shadow`}
                  >
                    {tier.popular && (
                      <div className="absolute top-0 left-1/2 transform -translate-x-1/2 -translate-y-1/2 px-4 py-1 bg-primary-600 text-white text-sm font-medium rounded-full shadow-sm">
                        Most Popular
                      </div>
                    )}
                    <h3 className="text-xl font-bold text-slate-900 dark:text-white mb-2">{tier.name}</h3>
                    <div className="flex items-baseline mb-4">
                      <span className="text-4xl font-bold text-slate-900 dark:text-white">{tier.price}</span>
                      <span className="ml-2 text-slate-500 dark:text-slate-400">/pass</span>
                    </div>
                    <p className="text-slate-600 dark:text-slate-400 mb-8">{tier.description}</p>
                    <ul className="space-y-4 mb-8 flex-grow">
                      {tier.features.map((feature, j) => (
                        <li key={j} className="flex items-start gap-3">
                          <Check className="w-5 h-5 text-primary-600 dark:text-primary-400 flex-shrink-0" />
                          <span className="text-sm text-slate-700 dark:text-slate-300">{feature}</span>
                        </li>
                      ))}
                    </ul>
                    <button 
                      onClick={() => handleSelectTier(tier)}
                      className={`w-full py-3 px-4 rounded-lg font-medium transition-colors ${tier.popular ? 'bg-primary-600 hover:bg-primary-700 text-white' : 'bg-slate-100 dark:bg-slate-800 text-slate-900 dark:text-white hover:bg-slate-200 dark:hover:bg-slate-700'}`}
                    >
                      Select Pass
                    </button>
                  </motion.div>
                ))}
              </div>
            </motion.div>
          )}

          {step === 'form' && selectedTier && (
            <motion.div 
              key="form" 
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -20 }}
              transition={{ duration: 0.4 }}
              className="max-w-2xl mx-auto"
            >
              <button 
                onClick={() => setStep('selection')}
                className="mb-8 flex items-center text-slate-500 hover:text-slate-900 dark:text-slate-400 dark:hover:text-white transition-colors"
              >
                <ArrowLeft className="w-4 h-4 mr-2" /> Back to Packages
              </button>

              <div className="bg-white dark:bg-slate-900 rounded-2xl border border-slate-200 dark:border-slate-800 shadow-sm p-8">
                <div className="mb-8 pb-8 border-b border-slate-200 dark:border-slate-800">
                  <h2 className="text-2xl font-bold text-slate-900 dark:text-white mb-2">Complete Registration</h2>
                  <p className="text-slate-600 dark:text-slate-400">
                    You are registering for the <span className="font-bold text-primary-600 dark:text-primary-400">{selectedTier.name} Pass</span> ({selectedTier.price}).
                  </p>
                </div>

                <form onSubmit={handleSubmit} className="space-y-6">
                  <div className="grid sm:grid-cols-2 gap-6">
                    <div>
                      <label className="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-2">
                        First Name
                      </label>
                      <div className="relative">
                        <User className="absolute left-3 top-3 h-5 w-5 text-slate-400" />
                        <input
                          type="text"
                          required
                          className="block w-full pl-10 pr-3 py-2.5 border border-slate-200 dark:border-slate-700 rounded-lg bg-slate-50 dark:bg-slate-800 text-slate-900 dark:text-white focus:ring-2 focus:ring-primary-500 focus:border-primary-500 transition-colors"
                          placeholder="Jane"
                          value={formData.firstName}
                          onChange={e => setFormData({...formData, firstName: e.target.value})}
                        />
                      </div>
                    </div>
                    <div>
                      <label className="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-2">
                        Last Name
                      </label>
                      <div className="relative">
                        <User className="absolute left-3 top-3 h-5 w-5 text-slate-400" />
                        <input
                          type="text"
                          required
                          className="block w-full pl-10 pr-3 py-2.5 border border-slate-200 dark:border-slate-700 rounded-lg bg-slate-50 dark:bg-slate-800 text-slate-900 dark:text-white focus:ring-2 focus:ring-primary-500 focus:border-primary-500 transition-colors"
                          placeholder="Doe"
                          value={formData.lastName}
                          onChange={e => setFormData({...formData, lastName: e.target.value})}
                        />
                      </div>
                    </div>
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-2">
                      Email Address
                    </label>
                    <div className="relative">
                      <Mail className="absolute left-3 top-3 h-5 w-5 text-slate-400" />
                      <input
                        type="email"
                        required
                        className="block w-full pl-10 pr-3 py-2.5 border border-slate-200 dark:border-slate-700 rounded-lg bg-slate-50 dark:bg-slate-800 text-slate-900 dark:text-white focus:ring-2 focus:ring-primary-500 focus:border-primary-500 transition-colors"
                        placeholder="jane@company.com"
                        value={formData.email}
                        onChange={e => setFormData({...formData, email: e.target.value})}
                      />
                    </div>
                  </div>

                  <div className="grid sm:grid-cols-2 gap-6">
                    <div>
                      <label className="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-2">
                        Company
                      </label>
                      <div className="relative">
                        <Building className="absolute left-3 top-3 h-5 w-5 text-slate-400" />
                        <input
                          type="text"
                          required
                          className="block w-full pl-10 pr-3 py-2.5 border border-slate-200 dark:border-slate-700 rounded-lg bg-slate-50 dark:bg-slate-800 text-slate-900 dark:text-white focus:ring-2 focus:ring-primary-500 focus:border-primary-500 transition-colors"
                          placeholder="Acme Inc."
                          value={formData.company}
                          onChange={e => setFormData({...formData, company: e.target.value})}
                        />
                      </div>
                    </div>
                    <div>
                      <label className="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-2">
                        Job Title
                      </label>
                      <div className="relative">
                        <User className="absolute left-3 top-3 h-5 w-5 text-slate-400" />
                        <input
                          type="text"
                          required
                          className="block w-full pl-10 pr-3 py-2.5 border border-slate-200 dark:border-slate-700 rounded-lg bg-slate-50 dark:bg-slate-800 text-slate-900 dark:text-white focus:ring-2 focus:ring-primary-500 focus:border-primary-500 transition-colors"
                          placeholder="Software Engineer"
                          value={formData.jobTitle}
                          onChange={e => setFormData({...formData, jobTitle: e.target.value})}
                        />
                      </div>
                    </div>
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-2">
                      Dietary Restrictions (Optional)
                    </label>
                    <div className="relative">
                      <Utensils className="absolute left-3 top-3 h-5 w-5 text-slate-400" />
                      <input
                        type="text"
                        className="block w-full pl-10 pr-3 py-2.5 border border-slate-200 dark:border-slate-700 rounded-lg bg-slate-50 dark:bg-slate-800 text-slate-900 dark:text-white focus:ring-2 focus:ring-primary-500 focus:border-primary-500 transition-colors"
                        placeholder="Gluten-free, Vegetarian, etc."
                        value={formData.dietary}
                        onChange={e => setFormData({...formData, dietary: e.target.value})}
                      />
                    </div>
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-2">
                      T-Shirt Size
                    </label>
                    <select
                      className="block w-full pl-3 pr-10 py-2.5 border border-slate-200 dark:border-slate-700 rounded-lg bg-slate-50 dark:bg-slate-800 text-slate-900 dark:text-white focus:ring-2 focus:ring-primary-500 focus:border-primary-500 transition-colors appearance-none"
                      value={formData.tshirt}
                      onChange={e => setFormData({...formData, tshirt: e.target.value})}
                    >
                      <option value="XS">XS</option>
                      <option value="S">S</option>
                      <option value="M">M</option>
                      <option value="L">L</option>
                      <option value="XL">XL</option>
                      <option value="2XL">2XL</option>
                      <option value="3XL">3XL</option>
                    </select>
                  </div>

                  <div className="pt-6 border-t border-slate-200 dark:border-slate-800 flex items-center justify-between">
                    <div>
                      <span className="block text-sm text-slate-500 dark:text-slate-400">Total Due</span>
                      <span className="text-2xl font-bold text-slate-900 dark:text-white">{selectedTier.price}</span>
                    </div>
                    <button
                      type="submit"
                      disabled={isSubmitting}
                      className="inline-flex items-center justify-center px-8 py-3 border border-transparent text-base font-medium rounded-lg text-white bg-primary-600 hover:bg-primary-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary-500 disabled:opacity-50 disabled:cursor-not-allowed transition-all shadow-lg shadow-primary-500/20"
                    >
                      {isSubmitting ? (
                        <>
                          <Loader2 className="animate-spin -ml-1 mr-3 h-5 w-5" />
                          Processing...
                        </>
                      ) : (
                        <>
                          <CreditCard className="-ml-1 mr-2 h-5 w-5" />
                          Complete Payment
                        </>
                      )}
                    </button>
                  </div>
                </form>
              </div>
            </motion.div>
          )}

          {step === 'success' && selectedTier && (
            <motion.div 
              key="success" 
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -20 }}
              transition={{ duration: 0.4 }}
              className="max-w-2xl mx-auto text-center pt-12"
            >
              <div className="inline-flex items-center justify-center w-24 h-24 rounded-full bg-green-100 dark:bg-green-900/30 text-green-600 dark:text-green-400 mb-8">
                <Check className="w-12 h-12" />
              </div>
              <h2 className="text-3xl font-bold text-slate-900 dark:text-white mb-4">You're all set!</h2>
              <p className="text-lg text-slate-600 dark:text-slate-400 mb-8">
                Thank you for registering, {formData.firstName}. We've sent a confirmation email to <span className="font-medium text-slate-900 dark:text-white">{formData.email}</span>.
              </p>
              
              <div className="bg-white dark:bg-slate-900 rounded-2xl border border-slate-200 dark:border-slate-800 p-8 mb-8 max-w-md mx-auto text-left shadow-sm">
                <h3 className="font-bold text-slate-900 dark:text-white mb-4 uppercase text-sm tracking-wider">Order Summary</h3>
                <div className="space-y-3 text-sm">
                  <div className="flex justify-between">
                    <span className="text-slate-500 dark:text-slate-400">Pass Type</span>
                    <span className="font-medium text-slate-900 dark:text-white">{selectedTier.name}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-slate-500 dark:text-slate-400">Attendee</span>
                    <span className="font-medium text-slate-900 dark:text-white">{formData.firstName} {formData.lastName}</span>
                  </div>
                  <div className="flex justify-between pt-3 border-t border-slate-100 dark:border-slate-800">
                    <span className="font-bold text-slate-900 dark:text-white">Total Paid</span>
                    <span className="font-bold text-primary-600 dark:text-primary-400">{selectedTier.price}</span>
                  </div>
                </div>
              </div>

              <div className="flex justify-center gap-4">
                <button 
                  onClick={() => navigate('/')}
                  className="px-6 py-3 rounded-lg font-medium text-slate-700 dark:text-slate-200 bg-white dark:bg-slate-800 border border-slate-200 dark:border-slate-700 hover:bg-slate-50 dark:hover:bg-slate-700 transition-colors"
                >
                  Return Home
                </button>
                <button 
                  onClick={() => navigate('/catalog')}
                  className="px-6 py-3 rounded-lg font-medium text-white bg-primary-600 hover:bg-primary-700 transition-colors shadow-lg shadow-primary-500/20"
                >
                  Browse Sessions
                </button>
              </div>
            </motion.div>
          )}
        </AnimatePresence>
      </div>
    </div>
  );
};