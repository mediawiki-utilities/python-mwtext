# Remove target files after command failure.
#.DELETE_ON_ERROR:

dump_dir=/mnt/data/xmldatadumps/public
dump_date=20191201


preprocessed_article_text: \
		datasets/arwiki-$(dump_date)-preprocessed_article_text.w_labels.txt \
		datasets/cswiki-$(dump_date)-preprocessed_article_text.w_labels.txt \
		datasets/enwiki-$(dump_date)-preprocessed_article_text.w_labels.txt \
		datasets/kowiki-$(dump_date)-preprocessed_article_text.w_labels.txt \
		datasets/viwiki-$(dump_date)-preprocessed_article_text.w_labels.txt

learned_vectors: \
		datasets/arwiki-$(dump_date)-learned_vectors.100_cell.300k.vec.bz2 \
		datasets/cswiki-$(dump_date)-learned_vectors.100_cell.300k.vec.bz2 \
		datasets/enwiki-$(dump_date)-learned_vectors.100_cell.300k.vec.bz2 \
		datasets/kowiki-$(dump_date)-learned_vectors.100_cell.300k.vec.bz2 \
		datasets/viwiki-$(dump_date)-learned_vectors.100_cell.300k.vec.bz2

datasets/enwiki.labeled_article_items.json.bz2:
	wget https://analytics.wikimedia.org/published/datasets/archive/public-datasets/all/ores/topic/enwiki-20191201-labeled_article_items.json.bz2 -qO- > $@


datasets/arwiki-$(dump_date)-preprocessed_article_text.w_labels.txt: \
		datasets/enwiki.labeled_article_items.json.bz2
	./utility preprocess_text $(dump_dir)/arwiki/$(dump_date)/arwiki-$(dump_date)-pages-articles[!-]*.xml-*.bz2 \
	 --namespace 0 \
	 --wiki-host https://ar.wikipedia.org \
	 --labels $^ \
	 --debug > $@

datasets/arwiki-$(dump_date)-learned_vectors.100_cell.vec.bz2: \
		datasets/arwiki-$(dump_date)-preprocessed_article_text.w_labels.txt
	./utility learn_vectors $^ \
	 --param 'dim=100' \
	 --param 'loss="ova"' | bzip2 -c > $@

datasets/arwiki-$(dump_date)-learned_vectors.100_cell.300k.vec.bz2: \
		datasets/arwiki-$(dump_date)-learned_vectors.100_cell.vec.bz2
	(echo "300000 100"; \
	 bzcat $^ | tail -n+2 | head -n 300000) | bzip2 -c > $@

datasets/cswiki-$(dump_date)-preprocessed_article_text.w_labels.txt: \
		datasets/enwiki.labeled_article_items.json.bz2
	./utility preprocess_text $(dump_dir)/cswiki/$(dump_date)/cswiki-$(dump_date)-pages-articles.xml.bz2 \
	 --namespace 0 \
	 --wiki-host https://cs.wikipedia.org \
	 --labels $^ \
	 --debug > $@

datasets/cswiki-$(dump_date)-learned_vectors.100_cell.vec.bz2: \
		datasets/cswiki-$(dump_date)-preprocessed_article_text.w_labels.txt
	./utility learn_vectors $^ \
	 --param 'dim=100' \
	 --param 'loss="ova"' | bzip2 -c > $@

datasets/cswiki-$(dump_date)-learned_vectors.100_cell.300k.vec.bz2: \
		datasets/cswiki-$(dump_date)-learned_vectors.100_cell.vec.bz2
	(echo "300000 100"; \
	 bzcat $^ | tail -n+2 | head -n 300000) | bzip2 -c > $@

datasets/enwiki-$(dump_date)-preprocessed_article_text.w_labels.txt: \
		datasets/enwiki.labeled_article_items.json.bz2
	./utility preprocess_text $(dump_dir)/enwiki/$(dump_date)/enwiki-$(dump_date)-pages-articles[!-]*.xml-*.bz2 \
	 --namespace 0 \
	 --wiki-host https://en.wikipedia.org \
	 --labels $^ \
	 --debug > $@

datasets/enwiki-$(dump_date)-learned_vectors.100_cell.vec.bz2: \
		datasets/enwiki-$(dump_date)-preprocessed_article_text.w_labels.txt
	./utility learn_vectors $^ \
	 --param 'dim=100' \
	 --param 'loss="ova"' | bzip2 -c > $@

datasets/enwiki-$(dump_date)-learned_vectors.100_cell.300k.vec.bz2: \
		datasets/enwiki-$(dump_date)-learned_vectors.100_cell.vec.bz2
	(echo "300000 100"; \
	 bzcat $^ | tail -n+2 | head -n 300000) | bzip2 -c > $@

datasets/kowiki-$(dump_date)-preprocessed_article_text.w_labels.txt: \
		datasets/enwiki.labeled_article_items.json.bz2
	./utility preprocess_text $(dump_dir)/kowiki/$(dump_date)/kowiki-$(dump_date)-pages-articles.xml.bz2 \
	 --namespace 0 \
	 --wiki-host https://ko.wikipedia.org \
	 --labels $^ \
	 --debug > $@

datasets/kowiki-$(dump_date)-learned_vectors.100_cell.vec.bz2: \
		datasets/kowiki-$(dump_date)-preprocessed_article_text.w_labels.txt
	./utility learn_vectors $^ \
	 --param 'dim=100' \
	 --param 'loss="ova"' | bzip2 -c > $@

datasets/kowiki-$(dump_date)-learned_vectors.100_cell.300k.vec.bz2: \
		datasets/kowiki-$(dump_date)-learned_vectors.100_cell.vec.bz2
	(echo "300000 100"; \
	 bzcat $^ | tail -n+2 | head -n 300000) | bzip2 -c > $@

datasets/viwiki-$(dump_date)-preprocessed_article_text.w_labels.txt: \
		datasets/enwiki.labeled_article_items.json.bz2
	./utility preprocess_text $(dump_dir)/viwiki/$(dump_date)/viwiki-$(dump_date)-pages-articles[!-]*.xml-*.bz2 \
	 --namespace 0 \
	 --wiki-host https://vi.wikipedia.org \
	 --labels $^ \
	 --debug > $@

datasets/viwiki-$(dump_date)-learned_vectors.100_cell.vec.bz2: \
		datasets/viwiki-$(dump_date)-preprocessed_article_text.w_labels.txt
	./utility learn_vectors $^ \
	 --param 'dim=100' \
	 --param 'loss="ova"' | bzip2 -c > $@

datasets/viwiki-$(dump_date)-learned_vectors.100_cell.300k.vec.bz2: \
		datasets/viwiki-$(dump_date)-learned_vectors.100_cell.vec.bz2
	(echo "300000 100"; \
	 bzcat $^ | tail -n+2 | head -n 300000) | bzip2 -c > $@
