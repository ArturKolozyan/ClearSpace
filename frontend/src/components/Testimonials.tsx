"use client";

import { motion } from "framer-motion";
import { Star, Quote } from "lucide-react";

const testimonials = [
  {
    id: 1,
    name: "Анна Смирнова",
    role: "Клиент",
    text: "Заказывала генеральную уборку после ремонта. Ребята справились на отлично! Отмыли всю строительную пыль, окна сияют. Очень довольна результатом.",
    rating: 5,
    avatar: "А",
    color: "bg-brand-blue",
  },
  {
    id: 2,
    name: "Дмитрий Иванов",
    role: "Владелец авто",
    text: "Делал химчистку салона. Машина как новая из салона! Убрали старые пятна с сидений, запах свежести держится уже неделю. Рекомендую.",
    rating: 5,
    avatar: "Д",
    color: "bg-brand-mint",
  },
  {
    id: 3,
    name: "Елена Петрова",
    role: "Клиент",
    text: "Регулярно заказываю поддерживающую уборку. Клинеры всегда приезжают вовремя, работают быстро и аккуратно. Эко-средства действительно не пахнут химией.",
    rating: 5,
    avatar: "Е",
    color: "bg-brand-lavender",
  },
];

export default function Testimonials() {
  return (
    <section id="testimonials" className="py-24 relative scroll-mt-24">
      <div className="container mx-auto px-4 sm:px-6 lg:px-8">
        <div className="text-center max-w-3xl mx-auto mb-16">
          <motion.h2
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true, margin: "-100px" }}
            transition={{ duration: 0.6 }}
            className="text-3xl md:text-4xl font-extrabold text-slate-900 mb-4"
          >
            Отзывы клиентов
          </motion.h2>
          <motion.p
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true, margin: "-100px" }}
            transition={{ duration: 0.6, delay: 0.1 }}
            className="text-lg text-slate-600 text-balance"
          >
            Что говорят о нас люди, которые уже доверили нам чистоту своего дома.
          </motion.p>
        </div>

        <div className="grid md:grid-cols-3 gap-8">
          {testimonials.map((testimonial, index) => (
            <motion.div
              key={testimonial.id}
              initial={{ opacity: 0, y: 20 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true, margin: "-100px" }}
              transition={{ duration: 0.5, delay: index * 0.1 }}
              className="glass-card p-8 relative text-center sm:text-left flex flex-col items-center sm:items-start"
            >
              <Quote className="absolute top-6 right-6 text-slate-200" size={48} />
              
              <div className="flex flex-col sm:flex-row items-center gap-4 mb-6">
                <div className={`w-14 h-14 rounded-2xl flex items-center justify-center text-white font-bold text-xl shadow-md ${testimonial.color}`}>
                  {testimonial.avatar}
                </div>
                <div className="text-center sm:text-left">
                  <h4 className="font-bold text-slate-900">{testimonial.name}</h4>
                  <p className="text-sm text-slate-500">{testimonial.role}</p>
                </div>
              </div>
              
              <div className="flex gap-1 mb-4 justify-center sm:justify-start">
                {[...Array(testimonial.rating)].map((_, i) => (
                  <Star key={i} size={18} className="fill-amber-400 text-amber-400" />
                ))}
              </div>
              
              <p className="text-slate-600 leading-relaxed italic relative z-10">
                &quot;{testimonial.text}&quot;
              </p>
            </motion.div>
          ))}
        </div>
      </div>
    </section>
  );
}