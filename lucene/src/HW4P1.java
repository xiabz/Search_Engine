import java.io.BufferedReader;
import java.io.BufferedWriter;
import java.io.File;
import java.io.FileReader;
import java.io.FileWriter;
import java.io.IOException;
import java.io.InputStreamReader;
import java.io.PrintWriter;
import java.util.ArrayList;
import java.util.HashMap;  
import java.util.Iterator;  
import java.util.Set;  
import java.util.Map.Entry;

import org.apache.lucene.analysis.Analyzer;
import org.apache.lucene.analysis.core.SimpleAnalyzer;
import org.apache.lucene.analysis.standard.StandardAnalyzer;
import org.apache.lucene.document.Document;
import org.apache.lucene.document.Field;
import org.apache.lucene.document.StringField;
import org.apache.lucene.document.TextField;
import org.apache.lucene.index.DirectoryReader;
import org.apache.lucene.index.IndexReader;
import org.apache.lucene.index.IndexWriter;
import org.apache.lucene.index.IndexWriterConfig;
import org.apache.lucene.index.Term;
import org.apache.lucene.queryparser.classic.QueryParser;
import org.apache.lucene.search.IndexSearcher;
import org.apache.lucene.search.Query;
import org.apache.lucene.search.ScoreDoc;
import org.apache.lucene.search.TopScoreDocCollector;
import org.apache.lucene.store.FSDirectory;
import org.apache.lucene.util.Version;

/**
 * To create Apache Lucene index in a folder and add files into this index based
 * on the input of the user.
 */
public class HW4P1 {
    private static Analyzer analyzer = new StandardAnalyzer(Version.LUCENE_47);
    private static Analyzer sAnalyzer = new SimpleAnalyzer(Version.LUCENE_47);

    private IndexWriter writer;
    private ArrayList<File> queue = new ArrayList<File>();
    private static HashMap<String,String> queries = new HashMap<String,String>();
    
    
    

    public static void main(String[] args) throws IOException {
    queries.put("1","global warming potential");
    queries.put("2","green power renewable energy");
    queries.put("3","solar energy california");
    queries.put("4","light bulb bulbs alternative alternatives");
    
	System.out
		.println("Enter the FULL path where the index will be created: (e.g. /Usr/index or c:\\temp\\index)");

	String indexLocation = null;
	BufferedReader br = new BufferedReader(new InputStreamReader(System.in));
	String s = br.readLine();

	HW4P1 indexer = null;
	try {
	    indexLocation = s;
	    indexer = new HW4P1(s);
	} catch (Exception ex) {
	    System.out.println("Cannot create index..." + ex.getMessage());
	    System.exit(-1);
	}
//    HashMap<String,String> br = new HashMap<String,String>();

	// ===================================================
	// read input from user until he enters q for quit
	// ===================================================
	while (!s.equalsIgnoreCase("q")) {
	    try {
		System.out
			.println("Enter the FULL path to add into the index (q=quit): (e.g. /home/mydir/docs or c:\\Users\\mydir\\docs)");
		System.out
			.println("[Acceptable file types: .xml, .html, .html, .txt]");
		s = br.readLine();
		if (s.equalsIgnoreCase("q")) {
		    break;
		}

		// try to add file into the index
		indexer.indexFileOrDirectory(s);
	    } catch (Exception e) {
		System.out.println("Error indexing " + s + " : "
			+ e.getMessage());
	    }
	}

	// ===================================================
	// after adding, we always have to call the
	// closeIndex, otherwise the index is not created
	// ===================================================
	indexer.closeIndex();

	// =========================================================
	// Now search
	// =========================================================
	IndexReader reader = DirectoryReader.open(FSDirectory.open(new File(
		indexLocation)));
	IndexSearcher searcher = new IndexSearcher(reader);
//	TopScoreDocCollector collector = TopScoreDocCollector.create(3, true);

/*	s = "";
	while (!s.equalsIgnoreCase("q")) {
	    try {
		System.out.println("Enter the search query (q=quit):");
		s = br.readLine();
		if (s.equalsIgnoreCase("q")) {
		    break;
		}*/
		
        Iterator it = queries.keySet().iterator();  
		while (it.hasNext()) {
			try {
				String key = (String) it.next();
				s = queries.get(key);

				Query q = new QueryParser(Version.LUCENE_47, "contents", sAnalyzer).parse(s);
				ScoreDoc[] hits = searcher.search(q, null, 100).scoreDocs;

				// 4. display results
				System.out.println("Found " + hits.length + " hits.");
				PrintWriter task = new PrintWriter("indexresult/Task1-" + key, "UTF-8");
				for (int i = 0; i < hits.length; ++i) {
					int docId = hits[i].doc;
					Document d = searcher.doc(docId);
				    String name = d.get("filename");
				    String documentId = name.substring(0, name.length() - 4);
					task.println(1 + " Q0" + " " + documentId + " " + (i + 1) + " " + hits[i].score + " lucene");
				}
				task.close();
	    } catch (Exception e) {
		System.out.println("Error searching " + s + " : " + e.getMessage());
		break;
	    } 
	}
    }

    /**
     * Constructor
     * 
     * @param indexDir
     *            the name of the folder in which the index should be created
     * @throws java.io.IOException
     *             when exception creating index.
     */
    HW4P1(String indexDir) throws IOException {

	FSDirectory dir = FSDirectory.open(new File(indexDir));

	IndexWriterConfig config = new IndexWriterConfig(Version.LUCENE_47,
		sAnalyzer);

	writer = new IndexWriter(dir, config);
    }

    /**
     * Indexes a file or directory
     * 
     * @param fileName
     *            the name of a text file or a folder we wish to add to the
     *            index
     * @throws java.io.IOException
     *             when exception
     */
    public void indexFileOrDirectory(String fileName) throws IOException {
	// ===================================================
	// gets the list of files in a folder (if user has submitted
	// the name of a folder) or gets a single file name (is user
	// has submitted only the file name)
	// ===================================================
	addFiles(new File(fileName));

	int originalNumDocs = writer.numDocs();
	for (File f : queue) {
	    FileReader fr = null;
	    try {
		Document doc = new Document();

		// ===================================================
		// add contents of file
		// ===================================================
		fr = new FileReader(f);
		doc.add(new TextField("contents", fr));
		doc.add(new StringField("path", f.getPath(), Field.Store.YES));
		doc.add(new StringField("filename", f.getName(),
			Field.Store.YES));

		writer.addDocument(doc);
		System.out.println("Added: " + f);
	    } catch (Exception e) {
		System.out.println("Could not add: " + f);
	    } finally {
		fr.close();
	    }
	}

	int newNumDocs = writer.numDocs();
	System.out.println("");
	System.out.println("************************");
	System.out
		.println((newNumDocs - originalNumDocs) + " documents added.");
	System.out.println("************************");

	queue.clear();
    }

    private void addFiles(File file) {

	if (!file.exists()) {
	    System.out.println(file + " does not exist.");
	}
	if (file.isDirectory()) {
	    for (File f : file.listFiles()) {
		addFiles(f);
	    }
	} else {
	    String filename = file.getName().toLowerCase();
	    // ===================================================
	    // Only index text files
	    // ===================================================
	    if (filename.endsWith(".htm") || filename.endsWith(".html")
		    || filename.endsWith(".xml") || filename.endsWith(".txt")) {
		queue.add(file);
	    } else {
		System.out.println("Skipped " + filename);
	    }
	}
    }

    /**
     * Close the index.
     * 
     * @throws java.io.IOException
     *             when exception closing
     */
    public void closeIndex() throws IOException {
	writer.close();
    }
}

