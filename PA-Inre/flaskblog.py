from flask import Flask, render_template,url_for
import functions as func
app = Flask(__name__)
# load

# load

posts =[
	{
		'author':'Fanta Ramot Sibarani',
		'title': 'Blog pertama',
		'content':'conten pertama',
		'date_posted':'April 20,2018'
	},
	{
		'author':'Melani Tambun',
		'title': 'Blog kedua',
		'content':'conten kedua',
		'date_posted':'April 20,2018'
	}

]

# tambahan


# @app.route('/')
# @app.route('/home')
# def home():
#     return render_template('home.html',posts=posts)

@app.route('/about')
def about():
    return render_template('about.html',title='About')
@app.route('/tes')
def tes():
    return render_template('tes.html',title='About')


# akhir tambahan


@app.route('/home')
def home():

	# if request.method == 'POST':
 #      user = request.form['nm']
 #      return redirect(url_for('success',name = user))
 #   else:
 #      user = request.args.get('nm')
 #      return redirect(url_for('success',name = user))

	# LOAD DATA
	location         = 'data/dataobat.xml'
	documentNumber   = func.docNumber(location)
	documentHeadline = func.docHeadline(location)
	documentText     = func.docText(location)
	documentTotal    = len(documentNumber)
	konten            = []


	for i in range(documentTotal):
	    konten.append(documentHeadline[i] + documentText[i])

	# PREPROCESSING
	text = func.removePunctuation(konten)
	text = func.caseFolding(text)
	text = func.tokenize(text)
	text = func.stopwordRemove(text)
	text = func.numberRemove(text)
	text = func.stemming(text)


	# GET ALL TERMS IN COLLECTION

	terms = func.getAllTerms(text)

	# INDEXING

	# index = createIndex(text,documentNumber, terms)
	index = func.createIndex(text,documentNumber)
	# tambahan untuk query yang belum di ekspan

	raw_query = ["100 mg of dacarbazine, "]
	# raw_query = newQuery

	query = func.removePunctuation(raw_query)
	query = func.caseFolding(query)
	query = func.tokenize(query)
	query = func.stopwordRemove(query)
	query = func.numberRemove(query)
	query = func.stemming(query)
	query = query[0]

	# Check Query In Index
	query = func.queryInIndex(query, index)

	# RANKED RETRIEVAL

	N               = documentTotal
	tfidf_list      = []

	docFrequency    = func.df(query, index)
	invDocFrequency = func.idf(docFrequency, N)
	termFrequency   = func.tf(query, index)
	TFIDF           = func.tfidf(termFrequency, invDocFrequency)
	sc              = func.score(TFIDF)

	relevanceDocNumber = []
	count = 0
	print('Query: ', raw_query,'\n\n')
	print('RESULTS: \n')

	for i in range(len(sc)):
	    relevanceDocNumber.append(int(sc[i]))
	    a = documentNumber.index(sc[i])
	    print(documentHeadline[a]+ 'Document Number: ',sc[i])

	#     print('\nContent:')
	#     print(documentText[a][0:400], '[read more]>>')
	    print('-------------------------------------------\n')
	    count = count + 1
	    if(count>=5):
	        break
	# akhir tambahan
	return render_template('home.html',title='Load_data', raw_query=raw_query, dh=documentHeadline)




if __name__=='__main__':
	app.run(debug=True)