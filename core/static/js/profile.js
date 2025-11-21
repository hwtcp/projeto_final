// profile.js
document.addEventListener('DOMContentLoaded', function () {
  // MASK CPF
  const cpfInput = document.querySelector('input[name="cpf"]');
  if (cpfInput) {
    cpfInput.addEventListener('input', function (e) {
      let v = e.target.value.replace(/\D/g, '');
      if (v.length > 11) v = v.slice(0,11);
      v = v.replace(/(\d{3})(\d)/, '$1.$2');
      v = v.replace(/(\d{3})(\d)/, '$1.$2');
      v = v.replace(/(\d{3})(\d{1,2})$/, '$1-$2');
      e.target.value = v;
    });
  }

  // MASK TELEFONE (brasil)
  const telInput = document.querySelector('input[name="telefone"]');
  if (telInput) {
    telInput.addEventListener('input', function (e) {
      let v = e.target.value.replace(/\D/g, '');
      if (v.length > 11) v = v.slice(0,11);
      if (v.length > 10) {
        v = v.replace(/(\d{2})(\d{5})(\d{4})/, '($1) $2-$3');
      } else {
        v = v.replace(/(\d{2})(\d{4})(\d{0,4})/, '($1) $2-$3');
      }
      e.target.value = v;
    });
  }

  // MASK peso e altura
  const peso = document.querySelector('input[name="peso"]');
  if (peso) {
    peso.addEventListener('input', function (e) {
      let v = e.target.value.replace(/[^0-9.,]/g, '').replace(',', '.');
      e.target.value = v;
    });
  }
  const altura = document.querySelector('input[name="altura"]');
  if (altura) {
    altura.addEventListener('input', function (e) {
      let v = e.target.value.replace(/[^0-9.,]/g, '').replace(',', '.');
      e.target.value = v;
    });
  }

  // FRONT CPF VALIDATION on submit (lightweight)
  const profileForm = document.getElementById('profile-form');
  if (profileForm) {
    profileForm.addEventListener('submit', function (e) {
      const cpfField = document.querySelector('input[name="cpf"]');
      if (cpfField) {
        const raw = cpfField.value.replace(/\D/g, '');
        if (raw.length && !validaCPF(raw)) {
          e.preventDefault();
          alert('CPF inválido. Verifique e tente novamente.');
          cpfField.focus();
          return false;
        }
      }
    });
  }

  // CPF validation algorithm (Brazil)
  function validaCPF(cpf) {
    if (!cpf || cpf.length !== 11) return false;
    if (/^(\d)\1+$/.test(cpf)) return false;
    let sum = 0, rest;
    for (let i = 1; i <= 9; i++) sum += parseInt(cpf.substring(i-1,i)) * (11 - i);
    rest = (sum * 10) % 11;
    if ((rest === 10) || (rest === 11)) rest = 0;
    if (rest !== parseInt(cpf.substring(9,10))) return false;
    sum = 0;
    for (let i = 1; i <= 10; i++) sum += parseInt(cpf.substring(i-1,i)) * (12 - i);
    rest = (sum * 10) % 11;
    if ((rest === 10) || (rest === 11)) rest = 0;
    if (rest !== parseInt(cpf.substring(10,11))) return false;
    return true;
  }
});
