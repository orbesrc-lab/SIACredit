import codecs
import re

path = r"c:\SIAC\templates\formacion.html"
with codecs.open(path, 'r', 'utf-8') as f:
    content = f.read()

pattern = r'(async function searchOpenLibrary\(\) \{)(.*?)(async function saveResource)'
def replacer(m):
    new_func = r"""
            const query = document.getElementById('openLibrarySearchQuery').value.trim();
            if(!query) return;
            
            const resultsDiv = document.getElementById('openLibraryResults');
            resultsDiv.style.display = 'grid';
            document.getElementById('savedResourcesContainer').style.display = 'none';
            resultsDiv.innerHTML = '<div style="grid-column: 1/-1; text-align: center; padding: 40px; color: #64748b;"><i class="fas fa-spinner fa-spin" style="font-size: 2rem; color: #6366f1; margin-bottom: 15px;"></i><br>Buscando en OpenAlex...</div>';
            
            try {
                const url = `https://api.openalex.org/works?search=${encodeURIComponent(query)}&filter=is_oa:true&per-page=20`;
                const response = await fetch(url);
                const data = await response.json();
                
                if(!data.results || data.results.length === 0) {
                    resultsDiv.innerHTML = '<div style="grid-column: 1/-1; text-align: center; padding: 40px; color: #64748b;">No se encontraron resultados de acceso abierto. Intenta usar otros términos.</div>';
                    return;
                }
                
                resultsDiv.innerHTML = '';
                data.results.forEach(work => {
                    const title = work.title || 'Sin título';
                    const year = work.publication_year || 'S.F.';
                    
                    let validAuthors = [];
                    if(work.authorships && work.authorships.length > 0) {
                        validAuthors = work.authorships.filter(a => a.author && a.author.display_name).map(a => a.author.display_name);
                    }
                    
                    let authorsStr = validAuthors.length > 0 ? validAuthors.slice(0, 3).join(', ') : 'Autor desconocido';
                    if(validAuthors.length > 3) authorsStr += ' et al.';
                    
                    const source = (work.primary_location && work.primary_location.source && work.primary_location.source.display_name) ? work.primary_location.source.display_name : 'Publicación Independiente';
                    const doi = work.doi || '';
                    const pdfUrl = (work.open_access && work.open_access.oa_url) ? work.open_access.oa_url : '';
                    
                    // APA 7
                    let apaCitation = '';
                    if(validAuthors.length > 0) {
                        const firstAuthorParts = validAuthors[0].split(' ');
                        const lastName = firstAuthorParts[firstAuthorParts.length-1];
                        const initials = firstAuthorParts.slice(0, firstAuthorParts.length-1).map(n => n.charAt(0)+'.').join(' ');
                        apaCitation = `${lastName}, ${initials} (${year}). <i>${title}</i>. ${source}. ${doi}`;
                    } else {
                        apaCitation = `${title}. (${year}). ${source}. ${doi}`;
                    }

                    const card = document.createElement('div');
                    card.style.cssText = 'background: white; border: 1px solid rgba(99,102,241,0.15); border-radius: 16px; padding: 20px; box-shadow: 0 4px 6px -1px rgba(0,0,0,0.05); display: flex; flex-direction: column; justify-content: space-between; transition: transform 0.2s, box-shadow 0.2s;';
                    card.onmouseover = () => { card.style.transform = 'translateY(-4px)'; card.style.boxShadow = '0 10px 15px -3px rgba(0,0,0,0.1)'; };
                    card.onmouseout = () => { card.style.transform = 'translateY(0)'; card.style.boxShadow = '0 4px 6px -1px rgba(0,0,0,0.05)'; };
                    
                    const safeTitle = title.replace(/'/g, "&#39;").replace(/"/g, "&quot;");
                    const safeAuthors = authorsStr.replace(/'/g, "&#39;").replace(/"/g, "&quot;");
                    const safeApa = apaCitation.replace(/'/g, "&#39;").replace(/"/g, "&quot;").replace(/<[^>]*>?/gm, '');

                    card.innerHTML = `
                        <div>
                            <span style="background: rgba(99,102,241,0.1); color: #4338ca; padding: 4px 10px; border-radius: 20px; font-size: 0.75rem; font-weight: 700; display: inline-block; margin-bottom: 10px;">
                                ${work.type === 'article' ? '📄 Artículo' : (work.type === 'book' ? '📘 Libro' : '📝 Documento')}
                            </span>
                            <h4 style="margin: 0 0 10px 0; font-size: 1.05rem; color: #0f172a; line-height: 1.3;">${title}</h4>
                            <p style="margin: 0 0 5px 0; font-size: 0.85rem; color: #64748b;"><i class="fas fa-users" style="margin-right:4px;"></i> ${authorsStr}</p>
                            <p style="margin: 0 0 15px 0; font-size: 0.85rem; color: #64748b;"><i class="fas fa-book-open" style="margin-right:4px;"></i> ${source} (${year})</p>
                            <div style="background: rgba(241,245,249,0.5); border-left: 3px solid #6366f1; padding: 10px; border-radius: 4px; font-size: 0.8rem; color: #475569; margin-bottom: 15px; word-break: break-word;">
                                <strong>APA 7.0:</strong><br> ${apaCitation}
                            </div>
                        </div>
                        <div style="display: flex; gap: 8px; flex-wrap: wrap;">
                            ${pdfUrl ? `<button class="btn-primary" onclick="window.open('${pdfUrl}', '_blank')" style="flex: 1; padding: 8px; font-size: 0.85rem; background: #10b981; border: none; box-shadow: 0 2px 4px rgba(16,185,129,0.3);"><i class="fas fa-external-link-alt"></i> Leer/PDF</button>` : `<button class="btn-primary" onclick="window.open('https://doi.org/${doi}', '_blank')" style="flex: 1; padding: 8px; font-size: 0.85rem; background: #64748b; border: none;"><i class="fas fa-link"></i> Ver Fuente</button>`}
                            <button class="btn-secondary" onclick="saveResource('${work.id}', '${safeTitle}', '${safeAuthors}', ${year}, '${pdfUrl || doi}', '${safeApa}')" style="flex: 1; padding: 8px; font-size: 0.85rem; border: 1px solid #cbd5e1; background: white;"><i class="far fa-star"></i> Guardar</button>
                        </div>
                    `;
                    resultsDiv.appendChild(card);
                });
            } catch (err) {
                console.error("OpenAlex Error:", err);
                resultsDiv.innerHTML = '<div style="grid-column: 1/-1; text-align: center; padding: 40px; color: #ef4444;"><i class="fas fa-exclamation-triangle" style="font-size:2rem; margin-bottom:10px;"></i><br>Error al buscar recursos. ' + err.message + '</div>';
            }
        }

        """
    return m.group(1) + new_func + m.group(3)

content = re.sub(pattern, replacer, content, flags=re.DOTALL)

with codecs.open(path, 'w', 'utf-8') as f:
    f.write(content)
print("Fixed searchOpenLibrary JS function")
