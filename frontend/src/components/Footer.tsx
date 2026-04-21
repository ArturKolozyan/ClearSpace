import Link from "next/link";
import Image from "next/image";
import { Phone } from "lucide-react";

export default function Footer() {
  return (
    <footer className="bg-slate-900 text-slate-300 py-16 border-t border-slate-800">
      <div className="container mx-auto px-4 sm:px-6 lg:px-8">
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-12 mb-12">
          {/* Brand */}
          <div className="col-span-1 lg:col-span-1">
            <Link href="/" className="flex items-center gap-2 mb-6">
              <div className="relative w-10 h-10 overflow-hidden rounded-xl bg-white">
                <Image
                  src="/logo.png"
                  alt="ClearSpace Logo"
                  fill
                  className="object-cover"
                  sizes="40px"
                />
              </div>
              <span className="font-heading font-bold text-xl text-white">
                ClearSpace
              </span>
            </Link>
            <p className="text-sm text-slate-400 mb-6 leading-relaxed">
              Профессиональный клининг для вашего дома и офиса. Мы делаем жизнь чище и комфортнее, освобождая ваше время для важных дел.
            </p>
          </div>

          {/* Links */}
          <div>
            <h4 className="text-white font-bold mb-6 uppercase tracking-wider text-sm">Услуги</h4>
            <ul className="space-y-3">
              <li><Link href="#services" className="text-sm hover:text-brand-blue transition-colors">Частные дома и квартиры</Link></li>
              <li><Link href="#services" className="text-sm hover:text-brand-blue transition-colors">Машины</Link></li>
              <li><Link href="#services" className="text-sm hover:text-brand-blue transition-colors">Мебель</Link></li>
            </ul>
          </div>

          {/* Company */}
          <div>
            <h4 className="text-white font-bold mb-6 uppercase tracking-wider text-sm">Компания</h4>
            <ul className="space-y-3">
              <li><Link href="#features" className="text-sm hover:text-brand-blue transition-colors">О нас</Link></li>
              <li><Link href="#portfolio" className="text-sm hover:text-brand-blue transition-colors">Наши работы</Link></li>
              <li><Link href="#testimonials" className="text-sm hover:text-brand-blue transition-colors">Отзывы</Link></li>
              <li><Link href="#faq" className="text-sm hover:text-brand-blue transition-colors">Вопросы и ответы</Link></li>
              <li><Link href="#contact" className="text-sm hover:text-brand-blue transition-colors">Контакты</Link></li>
            </ul>
          </div>

          {/* Contact */}
          <div>
            <h4 className="text-white font-bold mb-6 uppercase tracking-wider text-sm">Связаться с нами</h4>
            <ul className="space-y-4">
              <li className="flex items-start gap-3">
                <Phone size={20} className="text-brand-blue shrink-0 mt-0.5" />
                <div>
                  <a href="tel:+78000000000" className="text-sm hover:text-brand-blue transition-colors block mb-1">+7 (800) 000-00-00</a>
                  <span className="text-xs text-slate-500 block">Ежедневно с 9:00 до 21:00</span>
                </div>
              </li>
            </ul>
          </div>
        </div>

        <div className="pt-8 border-t border-slate-800 flex flex-col md:flex-row items-center justify-between gap-4">
          <p className="text-sm text-slate-500">
            &copy; {new Date().getFullYear()} ClearSpace. Все права защищены.
          </p>
          <div className="flex gap-6">
            <Link href="#" className="text-sm text-slate-500 hover:text-white transition-colors">Политика конфиденциальности</Link>
            <Link href="#" className="text-sm text-slate-500 hover:text-white transition-colors">Пользовательское соглашение</Link>
          </div>
        </div>
      </div>
    </footer>
  );
}