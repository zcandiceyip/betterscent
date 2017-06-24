import numpy as np

def get_ebay_link(perfume_string):
    """
    input: perfume_string, string
    returns: link to ebay page, string
    """
    import ebaysdk
    from ebaysdk.finding import Connection as finding
    
    api = finding(siteid='EBAY-US', 
                  appid='CandiceY-Bettersc-PRD-b8dfd86bc-41f85e11',
                  config_file=None)

    api.execute('findItemsAdvanced', {
        'keywords': perfume_string,
        'categoryId' : ['180345'],
        'paginationInput': {
            'entriesPerPage': '25',
            'pageNumber': '1' 
        },
        'sortOrder': 'CurrentPriceHighest'
    })

    dictstr = api.response.dict()
    return dictstr['itemSearchURL']


def get_recommendations_df(perfume_string, df, cos_matrix, evaluator):
    """
    inputs:
        perfume_string: str, input perfume to get recommendation for
        df: perfume database
        cos_df: dataframe; cosine similarity matrix
    returns: dataframe, ranked by highest recommendation
    """
    if perfume_string in list(df.name):
        # get index of perfume string
        perfume_string_index = df[df.name == perfume_string].index
        
        # get cos-similarity values for that perfume
        similarity_vals = cos_matrix[perfume_string_index]
        
        # get indices for cos-similarity values
        ranked_recs = np.argsort(similarity_vals)[0][:-22:-1]
        
        # get dataframe of top 20 most similar perfumes
        df_to_return = df.iloc[ranked_recs]
        df_to_return = df_to_return.drop(perfume_string_index)
        
        top_hit = df_to_return.sort_values(by='bayesian_rating', ascending=False).head(1)
        rec_name = top_hit.name.tolist()[0]
        
        rec_why = top_hit[evaluator].tolist()[0][2:-2].split("), ('")
        rec_why = rec_why[0].split("', '")

        
        orig_why = df.ix[perfume_string_index][evaluator].tolist()[0][2:-2].split("), ('")
        orig_why = orig_why[0].split("', '")

        image = top_hit.image
                
        final_why = []

        for i in orig_why:
            if i in rec_why:
                final_why.append(i)

        if len(final_why) == 1:
            statement = 'We recommend this fragrance because it shares ' + str(final_why[0]).lower() + ' notes with ' + str(perfume_string) + '.'
        else:
            new_s = ""
            for i in final_why[:-1]:
                new_s += (i + ', ')
            statement = 'We recommend this fragrance because it shares ' + new_s.lower() + ' and ' + str(final_why[-1]).lower() + ' notes with ' + str(perfume_string) + '.'

        ebay = get_ebay_link(rec_name)
        
        rating = round(top_hit.rating.tolist()[0], 2)
        
        rating_count = int(top_hit.rating_count.tolist()[0])
        
        return rec_name, statement, ebay, image.iloc[0], rating, rating_count
    
    else:
        rec_name = "Sorry, we don't have enough data about this fragrance to construct a recommendation."
        statement = None
        ebay = None
        image = None
        rating = None
        rating_count = None
        return rec_name, statement, ebay, image, rating, rating_count