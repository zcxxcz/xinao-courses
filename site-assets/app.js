'use strict';
const menu=document.querySelector('.menu-button');
const sidebar=document.querySelector('.sidebar');
const search=document.querySelector('#course-search');
const groups=[...sidebar.querySelectorAll('details')];
const initialOpen=groups.map(group=>group.open);
function setMenu(open){sidebar.classList.toggle('is-open',open);menu.setAttribute('aria-expanded',String(open));if(open)search.focus();}
menu.addEventListener('click',()=>setMenu(menu.getAttribute('aria-expanded')!=='true'));
document.addEventListener('keydown',event=>{if(event.key==='Escape'&&sidebar.classList.contains('is-open')){setMenu(false);menu.focus();}});
search.addEventListener('input',()=>{
 const term=search.value.trim().toLocaleLowerCase();let count=0;
 groups.forEach((group,index)=>{
  let visible=0;
  group.querySelectorAll('.nav-items a').forEach(link=>{
   const matches=!term||link.textContent.toLocaleLowerCase().includes(term)||group.querySelector('summary').textContent.toLocaleLowerCase().includes(term);
   link.hidden=!matches;if(matches)visible++;
  });
  group.hidden=visible===0;group.open=term?visible>0:initialOpen[index];count+=visible;
 });
 document.querySelector('.search-status').textContent=term?(count?`找到 ${count} 讲课程`:'没有匹配的课程，请换个关键词。'):'';
});
